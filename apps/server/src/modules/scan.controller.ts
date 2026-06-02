import { Body, Controller, Get, Post } from '@nestjs/common';

import { demoScan } from './demo-scan';
import { ScanRequestDto } from './scan.dto';
import { ScanService } from './scan.service';

@Controller('scans')
export class ScanController {
  private readonly scanService = new ScanService();

  @Post()
  createScan(@Body() body: ScanRequestDto) {
    return this.scanService.scan(body);
  }

  @Get('demo')
  getDemoScan() {
    return demoScan;
  }
}
