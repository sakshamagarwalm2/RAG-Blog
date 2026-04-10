import { Module } from '@nestjs/common';
import { IndexingController } from './indexing.controller';
import { IndexingService } from './indexing.service';
import { BlogsModule } from '../blogs/blogs.module';
import { VideosModule } from '../videos/videos.module';
import { IngestModule } from '../ingest/ingest.module';

@Module({
  imports: [BlogsModule, VideosModule, IngestModule],
  controllers: [IndexingController],
  providers: [IndexingService],
  exports: [IndexingService],
})
export class IndexingModule {}
