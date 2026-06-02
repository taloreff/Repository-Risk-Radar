import { CheckCircle2 } from 'lucide-react';

export function FindingEmptyState() {
  return (
    <div className="flex min-h-56 flex-col items-center justify-center p-6 text-center">
      <CheckCircle2 className="h-8 w-8 text-primary" aria-hidden="true" />
      <h3 className="mt-3 font-semibold">No vulnerabilities found</h3>
      <p className="mt-1 max-w-md text-sm text-muted-foreground">
        No OSV vulnerabilities were found for dependencies with exact resolved versions.
      </p>
    </div>
  );
}
