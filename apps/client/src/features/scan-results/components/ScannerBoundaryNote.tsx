import { ShieldQuestion } from 'lucide-react';

export function ScannerBoundaryNote() {
  return (
    <div className="rounded-lg border border-warning/30 bg-warning/10 p-4">
      <div className="flex gap-2">
        <ShieldQuestion className="mt-0.5 h-4 w-4 shrink-0 text-warning" aria-hidden="true" />
        <p className="text-sm text-warning">
          OpenVAS and Nmap are best reserved for assets you own and explicitly target. This UI
          keeps repository dependency analysis as the default scan path.
        </p>
      </div>
    </div>
  );
}
