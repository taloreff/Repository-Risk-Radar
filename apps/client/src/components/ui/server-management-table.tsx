'use client';

import { useMemo, useState } from 'react';

import { FindingDetailsOverlay } from '@/components/ui/server-management-table/FindingDetailsOverlay';
import { FindingEmptyState } from '@/components/ui/server-management-table/FindingEmptyState';
import { FindingManagementBody } from '@/components/ui/server-management-table/FindingManagementBody';
import { FindingManagementHeader } from '@/components/ui/server-management-table/FindingManagementHeader';
import type { Finding } from '@/lib/types';
import { cn } from '@/lib/utils';

type FindingManagementTableProps = {
  findings: Finding[];
  className?: string;
};

export function FindingManagementTable({ findings, className }: FindingManagementTableProps) {
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);
  const sortedFindings = useMemo(
    () => [...findings].sort((left, right) => right.risk_score - left.risk_score),
    [findings]
  );

  return (
    <div className={cn('relative overflow-hidden rounded-lg border bg-card text-card-foreground', className)}>
      <FindingManagementHeader count={findings.length} />
      {sortedFindings.length ? (
        <FindingManagementBody findings={sortedFindings} onSelectFinding={setSelectedFinding} />
      ) : (
        <FindingEmptyState />
      )}
      <FindingDetailsOverlay finding={selectedFinding} onClose={() => setSelectedFinding(null)} />
    </div>
  );
}
