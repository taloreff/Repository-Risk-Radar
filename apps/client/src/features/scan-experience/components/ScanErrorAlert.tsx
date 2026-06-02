import { AlertTriangle } from 'lucide-react';

export function ScanErrorAlert({ error }: { error: string | null }) {
  if (!error) {
    return null;
  }

  return (
    <div className="flex items-start gap-3 rounded-lg border border-danger/40 bg-danger/10 p-4 text-sm text-danger">
      <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
      <div className="space-y-2">
        <p>{error}</p>
        {error.includes('GitHub rate limit') ? (
          <p className="text-danger/80">
            Add `GITHUB_TOKEN` to the root `.env`, restart the server, or use Load demo while the
            unauthenticated limit resets.
          </p>
        ) : null}
      </div>
    </div>
  );
}
