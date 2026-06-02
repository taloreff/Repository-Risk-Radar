import type { ReactNode } from 'react';

import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';

import type { RiskVariant } from '../types/scan.types';

export function MetricCard({
  icon,
  label,
  value,
  tone
}: {
  icon: ReactNode;
  label: string;
  value: string | number;
  tone: RiskVariant;
}) {
  return (
    <Card>
      <CardContent className="p-5">
        <div className="flex items-center justify-between">
          <Badge variant={tone}>{icon}</Badge>
          <span className="text-xs uppercase tracking-wider text-muted-foreground">{label}</span>
        </div>
        <p className="mt-4 truncate text-3xl font-semibold">{value}</p>
      </CardContent>
    </Card>
  );
}
