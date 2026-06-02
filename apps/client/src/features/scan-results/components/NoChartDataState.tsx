import { ChartNoAxesCombined } from 'lucide-react';

import { EmptyState } from './EmptyState';

export function NoChartDataState() {
  return (
    <EmptyState
      icon={<ChartNoAxesCombined className="h-5 w-5" />}
      title="No scored findings"
      body="The agent did not find known vulnerabilities for dependencies with exact versions."
    />
  );
}
