import { Controller, Get, Post, Delete, Param, Body, HttpException, HttpStatus } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiProperty } from '@nestjs/swagger';
import { VideosService } from './videos.service';
import { ConfigService } from '@nestjs/config';

export class VideoCreateDto {
  @ApiProperty()
  youtube_url: string;
  @ApiProperty({ required: false })
  tags?: string[];
}

export class VideoManualCreateDto {
  @ApiProperty()
  youtube_url: string;
  @ApiProperty()
  transcript_raw: string;
  @ApiProperty({ required: false })
  tags?: string[];
}

@ApiTags('videos')
@Controller('videos')
export class VideosController {
  constructor(
    private readonly videosService: VideosService,
    private configService: ConfigService,
  ) {}

  @Get()
  @ApiOperation({ summary: 'Get all videos' })
  async getVideos() {
    return this.videosService.findAll();
  }

  @Post()
  @ApiOperation({ summary: 'Add a new video by URL' })
  async addVideo(@Body() payload: VideoCreateDto) {
    const videoId = this.videosService.extractVideoId(payload.youtube_url);
    const existing = await this.videosService.findByVideoId(videoId);
    if (existing) {
      throw new HttpException('This video has already been added.', HttpStatus.CONFLICT);
    }

    const metadata = await this.videosService.getMetadata(videoId);
    const { text: transcript_text, wordCount: word_count } = await this.videosService.getTranscript(videoId);

    const maxWords = parseInt(this.configService.get<string>('VIDEO_SUMMARY_MAX_WORDS', '3000'));
    let summary: string;
    let was_summarized = false;

    if (word_count > maxWords) {
      summary = await this.videosService.summarizeTranscript(transcript_text, metadata.title);
      was_summarized = true;
    } else {
      summary = transcript_text;
    }

    const videoData = {
      youtube_url: `https://www.youtube.com/watch?v=${videoId}`,
      video_id: videoId,
      title: metadata.title,
      channel: metadata.channel,
      thumbnail_url: metadata.thumbnail_url,
      transcript_raw: transcript_text,
      transcript_word_count: word_count,
      summary,
      was_summarized,
      tags: payload.tags || [],
    };

    return this.videosService.create(videoData);
  }

  @Post('manual')
  @ApiOperation({ summary: 'Add a video with manual transcript' })
  async addVideoManual(@Body() payload: VideoManualCreateDto) {
    const videoId = this.videosService.extractVideoId(payload.youtube_url);
    const existing = await this.videosService.findByVideoId(videoId);
    if (existing) {
      throw new HttpException('This video has already been added.', HttpStatus.CONFLICT);
    }

    const metadata = await this.videosService.getMetadata(videoId);
    const transcript_text = payload.transcript_raw.trim();
    const word_count = transcript_text.split(/\s+/).length;

    const maxWords = parseInt(this.configService.get<string>('VIDEO_SUMMARY_MAX_WORDS', '3000'));
    let summary: string;
    let was_summarized = false;

    if (word_count > maxWords) {
      summary = await this.videosService.summarizeTranscript(transcript_text, metadata.title);
      was_summarized = true;
    } else {
      summary = transcript_text;
    }

    const videoData = {
      youtube_url: `https://www.youtube.com/watch?v=${videoId}`,
      video_id: videoId,
      title: metadata.title,
      channel: metadata.channel,
      thumbnail_url: metadata.thumbnail_url,
      transcript_raw: transcript_text,
      transcript_word_count: word_count,
      summary,
      was_summarized,
      tags: payload.tags || [],
    };

    return this.videosService.create(videoData);
  }

  @Delete(':id')
  @ApiOperation({ summary: 'Delete a video' })
  async deleteVideo(@Param('id') id: string) {
    const deleted = await this.videosService.delete(id);
    if (!deleted) {
      throw new HttpException('Video not found', HttpStatus.NOT_FOUND);
    }
    return { deleted: true };
  }
}
