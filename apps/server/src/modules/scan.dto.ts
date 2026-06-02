import { BadRequestException } from '@nestjs/common';

export class ScanRequestDto {
  repoUrl!: string;
  noAi?: boolean;
}

export function validateScanRequest(request: ScanRequestDto) {
  if (!request.repoUrl || typeof request.repoUrl !== 'string') {
    throw new BadRequestException('Provide a valid GitHub repository URL.');
  }

  let parsed: URL;
  try {
    parsed = new URL(request.repoUrl);
  } catch {
    throw new BadRequestException('Provide a valid GitHub repository URL.');
  }

  if (parsed.protocol !== 'https:' || parsed.hostname !== 'github.com') {
    throw new BadRequestException('Only public https://github.com/owner/repo URLs are supported.');
  }
}
