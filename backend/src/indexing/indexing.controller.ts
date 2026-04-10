import { Controller, Get, Post, Query } from '@nestjs/common';
import { IndexingService } from './indexing.service';

@Controller('indexing')
export class IndexingController {
  constructor(private indexingService: IndexingService) {}

  @Get('status/blogs')
  async getBlogIndexingStatus() {
    return this.indexingService.getBlogIndexingStatus();
  }

  @Post('reindex')
  async reindex(@Query('force') force: string = 'false') {
    return this.indexingService.triggerReindex(force === 'true');
  }
}
