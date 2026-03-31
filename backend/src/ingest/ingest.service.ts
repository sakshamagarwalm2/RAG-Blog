import { Injectable } from '@nestjs/common';
import { BlogsService } from '../blogs/blogs.service';
import { VideosService } from '../videos/videos.service';
import { EmbeddingsService } from '../embeddings/embeddings.service';
import { VectorStoreService, Metadata } from '../vector-store/vector-store.service';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class IngestService {
  constructor(
    private blogsService: BlogsService,
    private videosService: VideosService,
    private embeddingsService: EmbeddingsService,
    private vectorStoreService: VectorStoreService,
    private configService: ConfigService,
  ) {}

  private chunkText(text: string, size: number, overlap: number): string[] {
    const chunks: string[] = [];
    if (!text || text.length < 50) return chunks;

    let start = 0;
    while (start < text.length) {
      const end = start + size;
      const chunk = text.slice(start, end);
      if (chunk.length >= 50) {
        chunks.push(chunk);
      }
      if (end >= text.length) break;
      start = end - overlap;
    }
    return chunks;
  }

  async rebuildIndex(): Promise<any> {
    const blogs = await this.blogsService.findAll();
    const videos = await this.videosService.findAll();

    const chunkSize = parseInt(this.configService.get<string>('CHUNK_SIZE', '500'));
    const chunkOverlap = parseInt(this.configService.get<string>('CHUNK_OVERLAP', '50'));
    const videoChunkSize = parseInt(this.configService.get<string>('VIDEO_CHUNK_SIZE', '600'));
    const videoChunkOverlap = parseInt(this.configService.get<string>('VIDEO_CHUNK_OVERLAP', '80'));

    const items: { embedding: number[]; metadata: Metadata }[] = [];

    for (const blog of blogs) {
      const chunks = this.chunkText(blog.content, chunkSize, chunkOverlap);
      for (let i = 0; i < chunks.length; i++) {
        const embedding = await this.embeddingsService.embedText(chunks[i]);
        items.push({
          embedding,
          metadata: {
            source_type: 'blog',
            source_id: (blog as any).id,
            title: blog.title,
            url: blog.url,
            chunk_text: chunks[i],
            chunk_index: i,
          },
        });
      }
    }

    for (const video of videos) {
      const chunks = this.chunkText(video.summary, videoChunkSize, videoChunkOverlap);
      for (let i = 0; i < chunks.length; i++) {
        const embedding = await this.embeddingsService.embedText(chunks[i]);
        items.push({
          embedding,
          metadata: {
            source_type: 'video',
            source_id: (video as any).id,
            video_id: video.video_id,
            title: video.title,
            url: `https://www.youtube.com/watch?v=${video.video_id}`,
            chunk_text: chunks[i],
            chunk_index: i,
            thumbnail_url: video.thumbnail_url,
            channel: video.channel,
          },
        });
      }
    }

    const result = await this.vectorStoreService.buildIndex(items);

    return {
      blogs: blogs.length,
      videos: videos.length,
      total_chunks: result.total_chunks,
    };
  }
}
