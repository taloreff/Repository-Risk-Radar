import * as React from 'react';

import { cn } from '@/lib/utils';

type ProgressProps = React.HTMLAttributes<HTMLDivElement> & {
  value: number;
};

export function Progress({ value, className, ...props }: ProgressProps) {
  const normalized = Math.max(0, Math.min(100, value));
  return (
    <div className={cn('h-2 w-full overflow-hidden rounded-sm bg-muted', className)} {...props}>
      <div
        className="h-full rounded-sm bg-primary transition-all"
        style={{ width: `${normalized}%` }}
      />
    </div>
  );
}
