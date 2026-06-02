import { Bot } from 'lucide-react';

import { Switch } from '@/components/ui/switch';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

export function AiSummaryToggle({
  checked,
  disabled,
  onCheckedChange
}: {
  checked: boolean;
  disabled: boolean;
  onCheckedChange: (checked: boolean) => void;
}) {
  return (
    <div className="flex items-center gap-2 text-sm text-muted-foreground">
      <Switch checked={checked} onCheckedChange={onCheckedChange} disabled={disabled} />
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <span className="inline-flex cursor-help items-center gap-2">
              <Bot className="h-4 w-4" aria-hidden="true" />
              <span className="underline decoration-primary/40 decoration-dotted underline-offset-4">
                AI summary
              </span>
            </span>
          </TooltipTrigger>
          <TooltipContent>
            Enabled: use for AI generated summary. Disabled: use the deterministic summary only.
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    </div>
  );
}
