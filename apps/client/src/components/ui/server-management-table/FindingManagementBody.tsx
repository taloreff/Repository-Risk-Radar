'use client';

import { motion, useReducedMotion } from 'framer-motion';

import { FindingManagementRow } from '@/components/ui/server-management-table/FindingManagementRow';
import { findingGrid } from '@/components/ui/server-management-table/findingTable.constants';
import type { Finding } from '@/lib/types';
import { cn } from '@/lib/utils';

export function FindingManagementBody({
  findings,
  onSelectFinding
}: {
  findings: Finding[];
  onSelectFinding: (finding: Finding) => void;
}) {
  const shouldReduceMotion = useReducedMotion();

  return (
    <div className="overflow-x-auto p-4">
      <motion.div
        className="min-w-[1040px] space-y-2"
        initial="hidden"
        animate="visible"
        variants={{ visible: { transition: { staggerChildren: shouldReduceMotion ? 0 : 0.045 } } }}
      >
        <div className={cn('grid gap-4 px-3 py-2 text-xs font-bold uppercase text-muted-foreground', findingGrid)}>
          <div>No</div>
          <div>Package</div>
          <div>Advisory</div>
          <div>Risk load</div>
          <div>CVSS</div>
          <div>EPSS</div>
          <div>Fix</div>
        </div>

        {findings.slice(0, 12).map((finding, index) => (
          <FindingManagementRow
            key={`${finding.dependency.name}-${finding.vulnerability.id}-${index}`}
            finding={finding}
            index={index}
            shouldReduceMotion={shouldReduceMotion}
            onSelect={() => onSelectFinding(finding)}
          />
        ))}
      </motion.div>
    </div>
  );
}
