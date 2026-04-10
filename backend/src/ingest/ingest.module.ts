import { Module } from '@nestjs/common';
import { IngestController } from './ingest.controller';
import { IngestService } from './ingest.service';
import { BlogsModule } from '../blogs/blogs.module';
import { VideosModule } from '../videos/videos.module';
import { EmbeddingsModule } from '../embeddings/embeddings.module';
import { VectorStoreModule } from '../vector-store/vector-store.module';

@Module({
  imports: [BlogsModule, VideosModule, EmbeddingsModule, VectorStoreModule],
  controllers: [IngestController],
  providers: [IngestService],
  exports: [IngestService],
})
export class IngestModule {}
