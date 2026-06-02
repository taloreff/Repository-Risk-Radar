import type { ScanResult } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:4000/api';

export async function runScan(repoUrl: string, noAi: boolean): Promise<ScanResult> {
  const response = await fetch(`${API_BASE_URL}/scans`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ repoUrl, noAi })
  });

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const message =
      data?.message?.message ?? data?.message ?? data?.error ?? 'The scan could not be completed.';
    throw new Error(typeof message === 'string' ? message : 'The scan could not be completed.');
  }

  return data as ScanResult;
}

export async function loadDemoScan(): Promise<ScanResult> {
  const response = await fetch(`${API_BASE_URL}/scans/demo`);
  if (!response.ok) {
    throw new Error('The demo scan could not be loaded.');
  }
  return (await response.json()) as ScanResult;
}
