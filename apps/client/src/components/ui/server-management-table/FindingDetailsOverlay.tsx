'use client';

import { AnimatePresence, motion } from 'framer-motion';
import { ExternalLink, ShieldAlert, X } from 'lucide-react';

import { FindingDetailStat } from '@/components/ui/server-management-table/FindingDetailStat';
import { highestCvss, highestEpss } from '@/components/ui/server-management-table/findingTable.utils';
import type { Finding } from '@/lib/types';
import { formatNumber, formatPercent } from '@/lib/utils';

export function FindingDetailsOverlay({ finding, onClose }: { finding: Finding | null; onClose: () => void }) {
  return (
    <AnimatePresence>
      {finding ? (
        <motion.div
          className="absolute inset-0 z-10 flex flex-col rounded-lg border bg-background/92 backdrop-blur-md"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <div className="flex items-start justify-between border-b bg-muted/30 p-5">
            <div className="flex gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-md border bg-card">
                <ShieldAlert className="h-5 w-5 text-primary" aria-hidden="true" />
              </div>
              <div>
                <h3 className="font-semibold">{finding.vulnerability.id}</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  {finding.dependency.name} · {finding.dependency.source_file}
                </p>
              </div>
            </div>
            <button type="button" onClick={onClose} className="flex h-8 w-8 items-center justify-center rounded-md border bg-card transition hover:bg-muted">
              <X className="h-4 w-4" aria-hidden="true" />
              <span className="sr-only">Close finding details</span>
            </button>
          </div>
          <div className="grid gap-4 overflow-y-auto p-5 md:grid-cols-3">
            <FindingDetailStat label="Risk score" value={finding.risk_score.toFixed(1)} />
            <FindingDetailStat label="CVSS" value={formatNumber(highestCvss(finding), 1)} />
            <FindingDetailStat label="EPSS" value={formatPercent(highestEpss(finding), 2)} />
            <div className="rounded-lg border bg-card p-4 md:col-span-3">
              <p className="text-xs uppercase text-muted-foreground">Summary</p>
              <p className="mt-2 text-sm leading-6">{finding.vulnerability.summary ?? 'No summary returned by OSV.'}</p>
            </div>
            <div className="rounded-lg border bg-card p-4 md:col-span-2">
              <p className="text-xs uppercase text-muted-foreground">Score reasons</p>
              <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
                {finding.reasons.map((reason) => <li key={reason}>{reason}</li>)}
              </ul>
            </div>
            <div className="rounded-lg border bg-card p-4">
              <p className="text-xs uppercase text-muted-foreground">Fix</p>
              <p className="mt-2 text-lg font-semibold">{finding.fixed_versions.join(', ') || 'unknown'}</p>
              {finding.vulnerability.references[0]?.url ? (
                <a href={finding.vulnerability.references[0].url} target="_blank" rel="noreferrer" className="mt-4 inline-flex items-center gap-2 text-sm text-primary hover:underline">
                  Reference
                  <ExternalLink className="h-3.5 w-3.5" aria-hidden="true" />
                </a>
              ) : null}
            </div>
          </div>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}
