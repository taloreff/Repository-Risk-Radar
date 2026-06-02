import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';

import type { ScanResult } from '../types/scan.types';
import { MiniStat } from './MiniStat';

export function ScanCoverageCard({
  scan,
  coverage
}: {
  scan: ScanResult;
  coverage: number;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Scan coverage</CardTitle>
        <CardDescription>Exact versions are required for precise OSV matching.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Dependencies checked</span>
            <span>
              {scan.stats.osv_queries}/{scan.dependencies.length}
            </span>
          </div>
          <Progress value={coverage} />
        </div>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
          <MiniStat label="Manifests" value={scan.manifests.length} />
          <MiniStat
            label="Skipped without exact versions"
            value={scan.stats.dependencies_without_resolved_versions}
          />
          <MiniStat label="NVD-enriched CVEs" value={scan.stats.cves_enriched} />
          <MiniStat label="EPSS-enriched CVEs" value={scan.stats.epss_enriched} />
        </div>
      </CardContent>
    </Card>
  );
}
