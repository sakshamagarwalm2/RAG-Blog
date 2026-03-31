import { Controller, Post } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { IngestService } from './ingest.service';

@ApiTags('ingest')
@Controller('ingest')
export class IngestController {
  constructor(private readonly ingestService: IngestService) {}

  @Post('rebuild')
  @ApiOperation({ summary: 'Rebuild the vector index from all blogs and videos' })
  async rebuildIndex() {
    return this.ingestService.rebuildIndex();
  }
}
