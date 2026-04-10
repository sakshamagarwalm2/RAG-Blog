import { Injectable } from '@nestjs/common';
import { BlogsService } from '../blogs/blogs.service';
import { VideosService } from '../videos/videos.service';
import { IngestService } from '../ingest/ingest.service';

@Injectable()
export class IndexingService {
  constructor(
    private blogsService: BlogsService,
    private videosService: VideosService,
    private ingestService: IngestService,
  ) {}

  async getBlogIndexingStatus() {
    const indexedBlogs = await this.blogsService.findIndexed();
    const unindexedBlogs = await this.blogsService.findUnindexed();
    return { indexed: indexedBlogs, unindexed: unindexedBlogs };
  }

  async triggerReindex(force: boolean = false) {
    return this.ingestService.rebuildIndex(force);
  }
}
