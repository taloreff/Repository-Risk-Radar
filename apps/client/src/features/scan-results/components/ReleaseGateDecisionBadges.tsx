import { Badge } from '@/components/ui/badge';

import type { ReleaseGate } from '../types/scan.types';
import { releaseGateVariant } from '../utils/severityStyles';

export function ReleaseGateDecisionBadges({ gate }: { gate: ReleaseGate }) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <Badge variant={releaseGateVariant(gate.decision)} className="px-3 py-1 font-mono text-lg">
        {gate.decision}
      </Badge>
      <Badge variant="secondary" className="font-mono">
        confidence {gate.confidence}
      </Badge>
      <Badge variant="secondary" className="font-mono">
        risk {gate.risk_score.toFixed(1)}
      </Badge>
    </div>
  );
}
