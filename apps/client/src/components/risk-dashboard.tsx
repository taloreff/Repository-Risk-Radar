'use client';

import { CveIntelligencePanel } from '@/features/scan-results/components/CveIntelligencePanel';
import { ExploitabilityMap } from '@/features/scan-results/components/ExploitabilityMap';
import { PrioritizedFindingsTable } from '@/features/scan-results/components/PrioritizedFindingsTable';
import { ReleaseGateCard } from '@/features/scan-results/components/ReleaseGateCard';
import { RemediationBriefCard } from '@/features/scan-results/components/RemediationBriefCard';
import { RiskMetricsGrid } from '@/features/scan-results/components/RiskMetricsGrid';
import { ScanCoverageCard } from '@/features/scan-results/components/ScanCoverageCard';
import type { ScanResult } from '@/features/scan-results/types/scan.types';
import {
  buildExploitabilityPoints,
  scanCoverage,
  uniqueCves
} from '@/features/scan-results/utils/riskFormatters';

export function RiskDashboard({ scan }: { scan: ScanResult }) {
  const coverage = scanCoverage(scan);
  const cves = uniqueCves(scan.findings);
  const chartData = buildExploitabilityPoints(scan.findings);

  return (
    <section className="space-y-6">
      {scan.release_gate ? <ReleaseGateCard gate={scan.release_gate} /> : null}

      <RiskMetricsGrid scan={scan} coverage={coverage} cves={cves} />

      <div className="grid gap-6 xl:grid-cols-[minmax(0,0.62fr)_minmax(360px,0.38fr)]">
        <ExploitabilityMap data={chartData} />
        <ScanCoverageCard scan={scan} coverage={coverage} />
      </div>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,0.58fr)_minmax(360px,0.42fr)]">
        <PrioritizedFindingsTable findings={scan.findings} />
        <RemediationBriefCard scan={scan} />
      </div>

      <CveIntelligencePanel cves={cves} />
    </section>
  );
}
