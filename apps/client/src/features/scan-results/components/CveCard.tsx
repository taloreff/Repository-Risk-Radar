import { Badge } from '@/components/ui/badge';
import { formatNumber, formatPercent } from '@/lib/utils';

import type { CveEnrichment } from '../types/scan.types';
import { nvdCveUrl } from '../utils/riskFormatters';
import { CveReferenceLink } from './CveReferenceLink';
import { MiniStat } from './MiniStat';

export function CveCard({ cve }: { cve: CveEnrichment }) {
  return (
    <div className="rounded-lg border bg-background/50 p-4">
      <div className="flex items-center justify-between gap-3">
        <a
          href={nvdCveUrl(cve.cve_id)}
          target="_blank"
          rel="noreferrer"
          className="font-mono font-bold text-primary underline decoration-primary/40 underline-offset-4 transition hover:text-foreground"
        >
          {cve.cve_id}
        </a>
        <Badge variant={cve.cisa_known_exploited ? 'danger' : 'secondary'}>
          {cve.cisa_known_exploited ? 'KEV' : cve.severity ?? 'unknown'}
        </Badge>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
        <MiniStat label="CVSS" value={formatNumber(cve.cvss_score, 1)} />
        <MiniStat label="EPSS" value={formatPercent(cve.epss_score, 2)} />
      </div>
      {cve.references[0] ? <CveReferenceLink href={cve.references[0]} /> : null}
    </div>
  );
}
