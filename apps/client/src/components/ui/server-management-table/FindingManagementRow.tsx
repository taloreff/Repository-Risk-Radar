'use client';

import { motion } from 'framer-motion';
import { Package } from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { RiskBars } from '@/components/ui/server-management-table/RiskBars';
import { findingGrid } from '@/components/ui/server-management-table/findingTable.constants';
import { highestCvss, highestEpss, riskGradient, riskTone } from '@/components/ui/server-management-table/findingTable.utils';
import type { Finding } from '@/lib/types';
import { cn, formatNumber, formatPercent } from '@/lib/utils';

export function FindingManagementRow({
  finding,
  index,
  shouldReduceMotion,
  onSelect
}: {
  finding: Finding;
  index: number;
  shouldReduceMotion: boolean | null;
  onSelect: () => void;
}) {
  return (
    <motion.button
      type="button"
      variants={{
        hidden: { opacity: 0, x: shouldReduceMotion ? 0 : -18, filter: shouldReduceMotion ? 'none' : 'blur(4px)' },
        visible: { opacity: 1, x: 0, filter: 'blur(0px)' }
      }}
      transition={{ type: 'spring', stiffness: 420, damping: 30 }}
      onClick={onSelect}
      className="group relative w-full overflow-hidden rounded-lg border bg-muted/35 p-3 text-left transition hover:-translate-y-0.5 hover:border-primary/55 hover:bg-muted/55 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
    >
      <div className={cn('absolute inset-y-0 right-0 w-48 bg-gradient-to-l opacity-70', riskGradient(finding.risk_level))} />
      <div className={cn('relative grid items-center gap-4', findingGrid)}>
        <div>
          <span className="font-mono text-2xl font-bold text-muted-foreground">
            {String(index + 1).padStart(2, '0')}
          </span>
        </div>
        <div className="min-w-0">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md border bg-background/70">
              <Package className="h-4 w-4 text-primary" aria-hidden="true" />
            </div>
            <div className="min-w-0">
              <p className="truncate font-bold" title={finding.dependency.name}>{finding.dependency.name}</p>
              <p className="truncate font-mono text-xs text-muted-foreground" title={finding.dependency.source_file}>
                {finding.dependency.source_file}
              </p>
            </div>
          </div>
        </div>
        <div className="min-w-0">
          <p className="truncate font-mono font-bold" title={finding.vulnerability.id}>{finding.vulnerability.id}</p>
          <p className="truncate text-xs text-muted-foreground" title={finding.vulnerability.summary ?? 'No summary returned'}>
            {finding.vulnerability.summary ?? 'No summary returned'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <RiskBars value={finding.risk_score} level={finding.risk_level} />
          <Badge variant={riskTone(finding.risk_level)} className="min-w-[70px] justify-center font-mono">
            {finding.risk_level} {finding.risk_score.toFixed(1)}
          </Badge>
        </div>
        <div className="font-mono text-sm font-bold">{formatNumber(highestCvss(finding), 1)}</div>
        <div className="font-mono text-sm font-bold">{formatPercent(highestEpss(finding), 2)}</div>
        <div className="truncate font-mono text-sm font-bold" title={finding.fixed_versions.join(', ') || 'unknown'}>
          {finding.fixed_versions[0] ?? 'unknown'}
        </div>
      </div>
    </motion.button>
  );
}
