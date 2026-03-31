import { Injectable, OnModuleInit, HttpException, HttpStatus } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { Video } from './schemas/video.schema';
import { ConfigService } from '@nestjs/config';
import * as ytdl from 'ytdl-core';
import { GoogleGenerativeAI } from '@google/generative-ai';

@Injectable()
export class VideosService implements OnModuleInit {
  private genAI: GoogleGenerativeAI;
  private geminiModel: string;
  private maxWords: number;

  constructor(
    @InjectModel(Video.name) private videoModel: Model<Video>,
    private configService: ConfigService,
  ) {}

  onModuleInit() {
    const apiKey = this.configService.get<string>('GEMINI_API_KEY');
    this.genAI = new GoogleGenerativeAI(apiKey);
    this.geminiModel = this.configService.get<string>('GEMINI_MODEL', 'gemini-2.5-flash');
    this.maxWords = parseInt(this.configService.get<string>('VIDEO_SUMMARY_MAX_WORDS', '3000'));
  }

  async findAll(): Promise<Video[]> {
    return this.videoModel.find().sort({ created_at: -1 }).exec();
  }

  async findByVideoId(videoId: string): Promise<Video> {
    return this.videoModel.findOne({ video_id: videoId }).exec();
  }

  async create(videoData: any): Promise<Video> {
    const newVideo = new this.videoModel(videoData);
    return newVideo.save();
  }

  async delete(id: string): Promise<boolean> {
    const result = await this.videoModel.findByIdAndDelete(id).exec();
    return !!result;
  }

  async getCount(): Promise<number> {
    return this.videoModel.countDocuments().exec();
  }

  extractVideoId(url: string): string {
    const pattern = /(?:v=|youtu\.be\/|embed\/|shorts\/)([a-zA-Z0-9_-]{11})/;
    const match = url.match(pattern);
    if (!match) {
      throw new HttpException('Invalid YouTube URL — could not extract video ID', HttpStatus.BAD_REQUEST);
    }
    return match[1];
  }

  async getMetadata(videoId: string): Promise<any> {
    try {
      // ytdl-core can be unstable, so we use a fallback title
      const info = await ytdl.getBasicInfo(`https://www.youtube.com/watch?v=${videoId}`);
      return {
        title: info.videoDetails.title || `YouTube Video (${videoId})`,
        channel: info.videoDetails.author.name || 'Unknown',
        thumbnail_url: `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`,
      };
    } catch (error) {
      return {
        title: `YouTube Video (${videoId})`,
        channel: 'Unknown',
        thumbnail_url: `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`,
      };
    }
  }

  async getTranscript(videoId: string): Promise<{ text: string; wordCount: number }> {
    try {
      const { YoutubeTranscript } = await import('youtube-transcript');
      const transcriptItems = await YoutubeTranscript.fetchTranscript(videoId);
      let text = transcriptItems.map((item) => item.text).join(' ');
      
      text = text.replace(/\[Music\]/g, '')
                 .replace(/\[Applause\]/g, '')
                 .replace(/\[Laughter\]/g, '')
                 .replace(/\n+/g, ' ')
                 .replace(/\s+/g, ' ')
                 .trim();
      
      const wordCount = text.split(/\s+/).length;
      if (wordCount < 10) {
        throw new Error('Transcript too short');
      }
      return { text, wordCount };
    } catch (error) {
      throw new HttpException('This video has no available transcript. Only videos with captions/subtitles can be added.', HttpStatus.BAD_REQUEST);
    }
  }

  async summarizeTranscript(transcript: string, title: string): Promise<string> {
    const prompt = `You are an expert content summarizer. Your task is to create a comprehensive, detailed summary of a YouTube video transcript.

Video Title: ${title}

Full Transcript:
${transcript}

Create a detailed summary that includes:
1. **Main Topic**: What is this video fundamentally about?
2. **Key Points**: List all major points covered (be thorough, include 8-15 bullet points)
3. **Important Details**: Specific facts, statistics, examples, code snippets, or techniques mentioned
4. **Concepts Explained**: Any technical concepts, terms, or frameworks introduced
5. **Practical Takeaways**: What can a viewer actually do or apply after watching this?
6. **Conclusions**: What conclusions or recommendations does the video make?

Write the summary in flowing paragraphs under each heading. Be detailed enough that someone who hasn't watched the video would fully understand all the content. Preserve technical accuracy — do not simplify or omit technical details.`;

    const model = this.genAI.getGenerativeModel({ model: this.geminiModel });
    
    for (let attempt = 0; attempt < 3; attempt++) {
      try {
        const result = await model.generateContent(prompt);
        return result.response.text();
      } catch (error) {
        if (attempt === 2) throw error;
        await new Promise((resolve) => setTimeout(resolve, 2000));
      }
    }
    return transcript;
  }
}
