import type { FormEvent } from 'react';
import { Github, Loader2, ScanLine } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

import { AiSummaryToggle } from './AiSummaryToggle';
import { RepoExamples } from './RepoExamples';

export function RepoScanForm({
  examples,
  loading,
  repoUrl,
  useAi,
  onLoadDemo,
  onRepoUrlChange,
  onScan,
  onUseAiChange
}: {
  examples: string[];
  loading: boolean;
  repoUrl: string;
  useAi: boolean;
  onLoadDemo: () => void;
  onRepoUrlChange: (repoUrl: string) => void;
  onScan: () => void;
  onUseAiChange: (useAi: boolean) => void;
}) {
  function submitScan(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onScan();
  }

  return (
    <form onSubmit={submitScan} className="rounded-lg border bg-background/80 p-2 shadow-2xl shadow-black/40">
      <div className="flex flex-col gap-2 sm:flex-row">
        <div className="relative flex-1">
          <Github className="pointer-events-none absolute left-3 top-3 h-5 w-5 text-muted-foreground" aria-hidden="true" />
          <Input
            value={repoUrl}
            onChange={(event) => onRepoUrlChange(event.target.value)}
            placeholder="https://github.com/owner/repo"
            className="h-12 pl-10"
            disabled={loading}
          />
        </div>
        <Button type="submit" className="h-12 min-w-32" disabled={loading || !repoUrl}>
          {loading ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <ScanLine className="h-4 w-4" aria-hidden="true" />}
          Scan
        </Button>
      </div>
      <div className="mt-3 flex flex-col gap-3 px-1 sm:flex-row sm:items-center sm:justify-between">
        <AiSummaryToggle checked={useAi} onCheckedChange={onUseAiChange} disabled={loading} />
        <RepoExamples examples={examples} onLoadDemo={onLoadDemo} onSelectRepo={onRepoUrlChange} />
      </div>
    </form>
  );
}
