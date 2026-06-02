import { Bug, Gauge, GitBranch, ShieldAlert } from 'lucide-react';

import type { CveEnrichment, ScanResult } from '../types/scan.types';
import { MetricCard } from './MetricCard';

export function RiskMetricsGrid({
  scan,
  coverage,
  cves
}: {
  scan: ScanResult;
  coverage: number;
  cves: CveEnrichment[];
}) {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <MetricCard
        icon={<Bug className="h-4 w-4" />}
        label="Findings"
        value={scan.findings.length}
        tone={scan.findings.length ? 'danger' : 'success'}
      />
      <MetricCard
        icon={<Gauge className="h-4 w-4" />}
        label="OSV coverage"
        value={`${coverage.toFixed(0)}%`}
        tone={coverage < 50 ? 'warning' : 'default'}
      />
      <MetricCard
        icon={<ShieldAlert className="h-4 w-4" />}
        label="CVEs"
        value={cves.length}
        tone={cves.length ? 'warning' : 'secondary'}
      />
      <MetricCard
        icon={<GitBranch className="h-4 w-4" />}
        label="Scanned ref"
        value={scan.scanned_ref}
        tone="secondary"
      />
    </div>
  );
}
