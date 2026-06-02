import { Module } from '@nestjs/common';

import { HealthController } from './health.controller';
import { ScanController } from './scan.controller';
import { ScanService } from './scan.service';

@Module({
  controllers: [HealthController, ScanController],
  providers: [ScanService],
})
export class AppModule {}
