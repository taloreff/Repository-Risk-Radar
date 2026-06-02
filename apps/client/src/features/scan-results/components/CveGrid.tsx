import type { CveEnrichment } from '../types/scan.types';
import { CveCard } from './CveCard';

export function CveGrid({ cves }: { cves: CveEnrichment[] }) {
  return (
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
      {cves.slice(0, 9).map((cve) => (
        <CveCard key={cve.cve_id} cve={cve} />
      ))}
    </div>
  );
}
