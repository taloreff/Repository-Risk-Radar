import type { ScanResult } from '@/lib/types';

import { CacheNotice } from './CacheNotice';
import { RepoScanForm } from './RepoScanForm';
import { ScanErrorAlert } from './ScanErrorAlert';

export function ScanHeroCard({
  error,
  examples,
  loading,
  repoUrl,
  scan,
  useAi,
  onLoadDemo,
  onRepoUrlChange,
  onScan,
  onUseAiChange
}: {
  error: string | null;
  examples: string[];
  loading: boolean;
  repoUrl: string;
  scan: ScanResult | null;
  useAi: boolean;
  onLoadDemo: () => void;
  onRepoUrlChange: (repoUrl: string) => void;
  onScan: () => void;
  onUseAiChange: (useAi: boolean) => void;
}) {
  return (
    <div className="security-surface flex min-h-[420px] flex-col justify-center rounded-lg border p-5 shadow-sm backdrop-blur sm:p-8">
      <div className="mx-auto flex w-full max-w-3xl flex-col gap-5">
        <div className="space-y-3 text-center">
          <h2 className="font-serif text-3xl leading-tight text-foreground sm:text-5xl">
            Scan dependency risk before it turns into release friction.
          </h2>
          <p className="mx-auto max-w-2xl text-sm leading-6 text-muted-foreground sm:text-base">
            Paste a public GitHub repository. The backend runs the Python agent, checks OSV,
            enriches CVEs with NVD and EPSS, then turns the result into a remediation board.
          </p>
          <CacheNotice cache={scan?.server_cache} />
        </div>
        <RepoScanForm
          examples={examples}
          loading={loading}
          repoUrl={repoUrl}
          useAi={useAi}
          onLoadDemo={onLoadDemo}
          onRepoUrlChange={onRepoUrlChange}
          onScan={onScan}
          onUseAiChange={onUseAiChange}
        />
        <ScanErrorAlert error={error} />
      </div>
    </div>
  );
}
