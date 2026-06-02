import { FileJson } from 'lucide-react';

export function CveReferenceLink({ href }: { href: string }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      className="mt-4 inline-flex items-center gap-2 text-sm text-primary hover:underline"
    >
      <FileJson className="h-4 w-4" aria-hidden="true" />
      Reference
    </a>
  );
}
