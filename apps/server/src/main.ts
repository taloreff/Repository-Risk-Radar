import 'reflect-metadata';

import { NestFactory } from '@nestjs/core';
import { config } from 'dotenv';
import { existsSync } from 'node:fs';
import path from 'node:path';

import { AppModule } from './modules/app.module';

loadRootEnv();

async function bootstrap() {
  const app = await NestFactory.create(AppModule, { cors: false });
  app.setGlobalPrefix('api');
  app.enableCors({
    origin: process.env.CLIENT_ORIGIN ?? 'http://localhost:3000',
  });

  const port = Number(process.env.PORT ?? 4000);
  await app.listen(port);
  console.log(`Repo Risk Radar API listening on http://localhost:${port}`);
}

void bootstrap();

function loadRootEnv() {
  const candidates = [
    path.resolve(process.cwd(), '.env'),
    path.resolve(process.cwd(), '../.env'),
    path.resolve(process.cwd(), '../../.env'),
  ];
  const envPath = candidates.find((candidate) => existsSync(candidate));
  if (envPath) {
    config({ path: envPath });
  }
}
