import { Injectable, Logger } from '@nestjs/common';
import { BlogsService } from '../blogs/blogs.service';
import { VideosService } from '../videos/videos.service';
import { EmbeddingsService } from '../embeddings/embeddings.service';
import { VectorStoreService, Metadata } from '../vector-store/vector-store.service';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class IngestService {
  private readonly logger = new Logger(IngestService.name);

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

  async rebuildIndex(force: boolean = false): Promise<any> {
    try {
      this.logger.log(`Starting indexing (force=${force})`);
      const blogs = await this.blogsService.findAll();
      const videos = await this.videosService.findAll();
      this.logger.log(`Found ${blogs.length} blogs and ${videos.length} videos in DB`);

      const indexedMetadataMap = force ? {} : this.vectorStoreService.getIndexedMetadataMap();
      const indexedIds = Object.keys(indexedMetadataMap);
      this.logger.log(`Found ${indexedIds.length} items already in index`);
      
      // Find items to delete (in index but not in DB)
      const dbBlogIds = blogs.map(b => (b as any).id || (b as any)._id?.toString());
      const dbVideoIds = videos.map(v => (v as any).id || (v as any)._id?.toString());
      const dbIds = new Set([...dbBlogIds, ...dbVideoIds]);
      
      let deletedCount = 0;
      if (!force) {
        for (const id of indexedIds) {
          if (!dbIds.has(id)) {
            this.logger.log(`Removing item ${id} from index (deleted from DB)`);
            await this.vectorStoreService.removeFromIndex(id);
            // Also update the indexed timestamp in the database
            if (id.startsWith('blog-')) {
              await this.blogsService.updateIndexedTimestamp(id.substring(5), null);
            }
            deletedCount++;
          }
        }
      } else {
        this.logger.log('Force rebuild: clearing index and unindexing all blogs');
        await this.vectorStoreService.buildIndex([]);
        await this.blogsService.setAllBlogsIndexedTimestamp(null);
      }

      const chunkSize = parseInt(this.configService.get<string>('CHUNK_SIZE', '500'));
      const chunkOverlap = parseInt(this.configService.get<string>('CHUNK_OVERLAP', '50'));
      const videoChunkSize = parseInt(this.configService.get<string>('VIDEO_CHUNK_SIZE', '600'));
      const videoChunkOverlap = parseInt(this.configService.get<string>('VIDEO_CHUNK_OVERLAP', '80'));

      let newlyIndexedBlogs = 0;
      let newlyIndexedVideos = 0;
      let totalChunksAdded = 0;

      for (const blog of blogs) {
        const blogId = (blog as any).id || (blog as any)._id?.toString();
        
        // Determine if blog needs indexing based on indexed_at and updated_at
        const needsIndexing = !blog.indexed_at || (blog.updated_at && blog.updated_at > blog.indexed_at);

        if (force || needsIndexing) {
          this.logger.log(`Indexing blog ${blogId} (needsIndexing=${needsIndexing})`);
          // If already indexed but content updated, remove old entries first
          if (blog.indexed_at) { // meaning it was previously indexed
            await this.vectorStoreService.removeFromIndex(blogId);
          }

          const chunks = this.chunkText(blog.content, chunkSize, chunkOverlap);
          const items: { embedding: number[]; metadata: Metadata }[] = [];
          
          for (let i = 0; i < chunks.length; i++) {
            const embedding = await this.embeddingsService.embedText(chunks[i]);
            items.push({
              embedding,
              metadata: {
                source_type: 'blog',
                source_id: blogId,
                title: blog.title,
                url: blog.url,
                chunk_text: chunks[i],
                chunk_index: i,
                updated_at: blog.updated_at?.toISOString() || new Date().toISOString(),
              },
            });
          }
          
          if (items.length > 0) {
            await this.vectorStoreService.addToIndex(items);
            newlyIndexedBlogs++;
            totalChunksAdded += items.length;
            // Update blog's indexed timestamp
            await this.blogsService.updateIndexedTimestamp(blogId, new Date());
          }
        }
      }

      for (const video of videos) {
        const videoId = (video as any).id || (video as any)._id?.toString();
        const lastIndexed = indexedMetadataMap[videoId];
        
        const isNew = !lastIndexed;
        const isUpdated = lastIndexed && video.updated_at && new Date(video.updated_at) > new Date(lastIndexed.updated_at);

        if (force || isNew || isUpdated) {
          this.logger.log(`Indexing video ${videoId} (isNew=${isNew}, isUpdated=${isUpdated})`);
          if (isUpdated) {
            await this.vectorStoreService.removeFromIndex(videoId);
          }

          const chunks = this.chunkText(video.summary, videoChunkSize, videoChunkOverlap);
          const items: { embedding: number[]; metadata: Metadata }[] = [];
          
          for (let i = 0; i < chunks.length; i++) {
            const embedding = await this.embeddingsService.embedText(chunks[i]);
            items.push({
              embedding,
              metadata: {
                source_type: 'video',
                source_id: videoId,
                video_id: video.video_id,
                title: video.title,
                url: `https://www.youtube.com/watch?v=${video.video_id}`,
                chunk_text: chunks[i],
                chunk_index: i,
                thumbnail_url: video.thumbnail_url,
                channel: video.channel,
                updated_at: video.updated_at?.toISOString() || new Date().toISOString(),
              },
            });
          }
          
          if (items.length > 0) {
            await this.vectorStoreService.addToIndex(items);
            newlyIndexedVideos++;
            totalChunksAdded += items.length;
          }
        }
      }

      return {
        blogs: blogs.length,
        videos: videos.length,
        newly_indexed_blogs: newlyIndexedBlogs,
        newly_indexed_videos: newlyIndexedVideos,
        deleted_from_index: deletedCount,
        total_chunks_added: totalChunksAdded,
      };
    } catch (error: any) {
      this.logger.error(`Error during indexing: ${error.message}`, error.stack);
      throw error;
    }
  }
}
