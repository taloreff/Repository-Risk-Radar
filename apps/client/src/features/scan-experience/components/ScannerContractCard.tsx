import { Card, CardContent } from '@/components/ui/card';

import { StatusLine } from './StatusLine';

export function ScannerContractCard() {
  return (
    <Card className="security-surface backdrop-blur">
      <CardContent className="flex h-full flex-col justify-between gap-6 p-5">
        <div className="space-y-2">
          <p className="text-sm text-muted-foreground">Scanner contract</p>
          <h2 className="font-serif text-2xl">Deterministic data first, AI second.</h2>
          <p className="text-sm leading-6 text-muted-foreground">
            GitHub manifests, OSV matching, NVD enrichment, EPSS probability, and the risk score
            are all structured agent output. The language model only writes narrative summaries
            and remediation framing.
          </p>
        </div>
        <div className="grid gap-3 text-sm">
          <StatusLine label="Dependency source" value="package.json, lockfiles, pyproject, requirements" />
          <StatusLine label="Risk signals" value="CVSS, EPSS, CISA KEV, directness, fixes" />
          <StatusLine label="Network scanners" value="OpenVAS/Nmap kept as opt-in future integrations" />
        </div>
      </CardContent>
    </Card>
  );
}
