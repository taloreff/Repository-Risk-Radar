import { BadRequestException, Injectable, InternalServerErrorException } from '@nestjs/common';
import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import path from 'node:path';

import { ScanRequestDto, validateScanRequest } from './scan.dto';

type AgentProcessResult = {
  stdout: string;
  stderr: string;
};

type CachedScan = {
  expiresAt: number;
  value: Record<string, unknown>;
};

const scanCache = new Map<string, CachedScan>();
const inflightScans = new Map<string, Promise<Record<string, unknown>>>();

@Injectable()
export class ScanService {
  async scan(request: ScanRequestDto) {
    validateScanRequest(request);

    const cacheKey = createCacheKey(request);
    const cached = getCachedScan(cacheKey);
    if (cached) {
      return withCacheMetadata(cached, true);
    }

    const inflight = inflightScans.get(cacheKey);
    if (inflight) {
      return withCacheMetadata(await inflight, true);
    }

    const scanPromise = this.runFreshScan(request);
    inflightScans.set(cacheKey, scanPromise);
    try {
      const fresh = await scanPromise;
      setCachedScan(cacheKey, fresh);
      return withCacheMetadata(fresh, false);
    } finally {
      inflightScans.delete(cacheKey);
    }
  }

  private async runFreshScan(request: ScanRequestDto): Promise<Record<string, unknown>> {
    const agentDir = findAgentDir();
    const python = envValue('AGENT_PYTHON') ?? findPython();
    const args = ['-m', 'repo_risk_radar', 'analyze', request.repoUrl, '--json'];
    if (request.noAi) {
      args.push('--no-ai');
    }

    const result = await runAgent(python, args, agentDir);
    try {
      return JSON.parse(result.stdout) as Record<string, unknown>;
    } catch (error) {
      throw new InternalServerErrorException({
        message: 'The Python agent returned non-JSON output.',
        stderr: result.stderr,
        error: error instanceof Error ? error.message : String(error),
      });
    }
  }
}

function createCacheKey(request: ScanRequestDto): string {
  return JSON.stringify({
    repoUrl: request.repoUrl.trim().replace(/\/$/, ''),
    noAi: Boolean(request.noAi),
  });
}

function getCachedScan(cacheKey: string): Record<string, unknown> | null {
  const cached = scanCache.get(cacheKey);
  if (!cached) {
    return null;
  }
  if (Date.now() > cached.expiresAt) {
    scanCache.delete(cacheKey);
    return null;
  }
  return cached.value;
}

function setCachedScan(cacheKey: string, value: Record<string, unknown>) {
  scanCache.set(cacheKey, {
    expiresAt: Date.now() + cacheTtlMs(),
    value,
  });
}

function withCacheMetadata(scan: Record<string, unknown>, hit: boolean) {
  return {
    ...scan,
    server_cache: {
      hit,
      ttl_seconds: Math.round(cacheTtlMs() / 1000),
    },
  };
}

function cacheTtlMs(): number {
  const seconds = Number(envValue('SCAN_CACHE_TTL_SECONDS') ?? 900);
  return Number.isFinite(seconds) && seconds > 0 ? seconds * 1000 : 900_000;
}

function envValue(name: string): string | undefined {
  const value = process.env[name]?.trim();
  return value ? value : undefined;
}

function runAgent(command: string, args: string[], cwd: string): Promise<AgentProcessResult> {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      cwd,
      env: { ...process.env, PYTHONUNBUFFERED: '1' },
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    let stdout = '';
    let stderr = '';
    const timeout = setTimeout(() => {
      child.kill('SIGTERM');
      reject(new InternalServerErrorException('Scan timed out after 120 seconds.'));
    }, 120_000);

    child.stdout.on('data', (chunk) => {
      stdout += chunk.toString();
    });
    child.stderr.on('data', (chunk) => {
      stderr += chunk.toString();
    });
    child.on('error', (error) => {
      clearTimeout(timeout);
      reject(new InternalServerErrorException(error.message));
    });
    child.on('close', (code) => {
      clearTimeout(timeout);
      if (code === 0) {
        resolve({ stdout, stderr });
        return;
      }
      reject(
        new BadRequestException({
          message: parseAgentError(stderr) ?? 'Agent scan failed.',
          stderr,
        }),
      );
    });
  });
}

function parseAgentError(stderr: string): string | undefined {
  const match = stderr.match(/Error:\s*(.+)/);
  return match?.[1]?.trim();
}

function findAgentDir(): string {
  const candidates = [
    path.resolve(process.cwd(), '../agent'),
    path.resolve(process.cwd(), 'apps/agent'),
    path.resolve(process.cwd(), '../../apps/agent'),
  ];
  const found = candidates.find((candidate) => existsSync(path.join(candidate, 'pyproject.toml')));
  if (!found) {
    throw new InternalServerErrorException('Could not locate apps/agent.');
  }
  return found;
}

function findPython(): string {
  const candidates = [
    path.resolve(process.cwd(), '../../.venv/bin/python'),
    path.resolve(process.cwd(), '../.venv/bin/python'),
    path.resolve(process.cwd(), '.venv/bin/python'),
  ];
  return candidates.find((candidate) => existsSync(candidate)) ?? 'python3';
}
