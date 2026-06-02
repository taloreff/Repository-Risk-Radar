import { Radar, ShieldCheck } from 'lucide-react';

import { AnimatedThemeToggleButton } from '@/components/ui/animated-theme-toggle-button';
import { Badge } from '@/components/ui/badge';

export function ScanHeader() {
  return (
    <header className="flex items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg border bg-card shadow-sm shadow-primary/10">
          <Radar className="h-5 w-5 text-primary" aria-hidden="true" />
        </div>
        <div>
          <p className="text-sm text-muted-foreground">Repo Risk Radar</p>
          <h1 className="font-serif text-xl">Dependency intelligence cockpit</h1>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <Badge variant="success" className="hidden bg-primary/10 text-primary sm:inline-flex">
          <ShieldCheck className="mr-1 h-3.5 w-3.5" aria-hidden="true" />
          Defensive only
        </Badge>
        <AnimatedThemeToggleButton type="vertical" />
      </div>
    </header>
  );
}
