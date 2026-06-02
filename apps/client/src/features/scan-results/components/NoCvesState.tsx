import { AlertTriangle } from 'lucide-react';

import { EmptyState } from './EmptyState';

export function NoCvesState() {
  return (
    <EmptyState
      icon={<AlertTriangle className="h-5 w-5" />}
      title="No CVEs returned"
      body="Some OSV advisories are GHSA-only. CVE enrichment appears here when aliases exist."
    />
  );
}
