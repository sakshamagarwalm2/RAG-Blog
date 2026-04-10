import { Controller, Post, Query } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiQuery } from '@nestjs/swagger';
import { IngestService } from './ingest.service';

@ApiTags('ingest')
@Controller('ingest')
export class IngestController {
  constructor(private readonly ingestService: IngestService) {}

  @Post('rebuild')
  @ApiOperation({ summary: 'Rebuild or update the vector index incrementally' })
  @ApiQuery({ name: 'force', type: Boolean, required: false, description: 'Force full rebuild' })
  async rebuildIndex(@Query('force') force?: string) {
    const isForce = force === 'true';
    return this.ingestService.rebuildIndex(isForce);
  }
}
