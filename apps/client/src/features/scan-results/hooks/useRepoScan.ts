'use client';

import { useState } from 'react';

import { loadDemoScan, runScan } from '@/lib/api';
import type { ScanResult } from '@/lib/types';

import { DEFAULT_REPO_URL, EXAMPLE_REPOS } from '../../scan-experience/constants';

export function useRepoScan() {
  const [repoUrl, setRepoUrl] = useState(DEFAULT_REPO_URL);
  const [useAi, setUseAi] = useState(true);
  const [scan, setScan] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function scanRepo() {
    setError(null);
    setLoading(true);
    try {
      setScan(await runScan(repoUrl, !useAi));
    } catch (scanError) {
      setError(scanError instanceof Error ? scanError.message : 'Scan failed.');
    } finally {
      setLoading(false);
    }
  }

  async function loadDemo() {
    setError(null);
    setLoading(true);
    try {
      setScan(await loadDemoScan());
    } catch (demoError) {
      setError(demoError instanceof Error ? demoError.message : 'Demo failed.');
    } finally {
      setLoading(false);
    }
  }

  return {
    error,
    examples: EXAMPLE_REPOS,
    loading,
    loadDemo,
    repoUrl,
    scan,
    scanRepo,
    setRepoUrl,
    setUseAi,
    useAi
  };
}
