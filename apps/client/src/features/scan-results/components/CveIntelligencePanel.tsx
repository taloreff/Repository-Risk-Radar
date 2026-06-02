import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

import type { CveEnrichment } from '../types/scan.types';
import { CveGrid } from './CveGrid';
import { NoCvesState } from './NoCvesState';

export function CveIntelligencePanel({ cves }: { cves: CveEnrichment[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>CVE intelligence</CardTitle>
        <CardDescription>NVD severity plus EPSS likelihood when the CVE exposes it.</CardDescription>
      </CardHeader>
      <CardContent>
        {cves.length ? <CveGrid cves={cves} /> : <NoCvesState />}
      </CardContent>
    </Card>
  );
}
