import { ClipboardCheck, Copy } from 'lucide-react';

import { Button } from '@/components/ui/button';

export function DeveloperTicketPanel({
  ticketText,
  copied,
  aiGenerated,
  onCopy
}: {
  ticketText: string;
  copied: boolean;
  aiGenerated: boolean;
  onCopy: () => void;
}) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h3 className="text-base">Developer ticket</h3>
          <p className="text-sm text-muted-foreground">
            {aiGenerated ? 'AI formatted from policy evidence.' : 'Deterministic fallback.'}
          </p>
        </div>
        <Button type="button" size="sm" variant="outline" onClick={onCopy}>
          {copied ? (
            <ClipboardCheck className="h-4 w-4" aria-hidden="true" />
          ) : (
            <Copy className="h-4 w-4" aria-hidden="true" />
          )}
          {copied ? 'Copied' : 'Copy'}
        </Button>
      </div>
      <pre className="max-h-96 overflow-auto whitespace-pre-wrap rounded-lg border bg-background/60 p-4 font-mono text-xs leading-5 text-muted-foreground">
        {ticketText}
      </pre>
    </div>
  );
}
