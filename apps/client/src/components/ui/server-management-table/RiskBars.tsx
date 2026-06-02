import { riskBarColor } from '@/components/ui/server-management-table/findingTable.utils';
import type { Finding } from '@/lib/types';
import { cn } from '@/lib/utils';

export function RiskBars({ value, level }: { value: number; level: Finding['risk_level'] }) {
  const filledBars = Math.max(1, Math.round((Math.min(value, 100) / 100) * 10));

  return (
    <div className="flex shrink-0 gap-1" aria-hidden="true">
      {Array.from({ length: 10 }).map((_, index) => (
        <div
          key={index}
          className={cn('h-5 w-1.5 rounded-full border transition', index < filledBars
            ? riskBarColor(level)
            : 'border-border/40 bg-background/70')}
        />
      ))}
    </div>
  );
}
