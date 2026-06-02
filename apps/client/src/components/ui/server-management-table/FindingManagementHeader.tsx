import { Badge } from '@/components/ui/badge';

export function FindingManagementHeader({ count }: { count: number }) {
  return (
    <div className="flex flex-col gap-3 border-b px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-primary" />
          <h3 className="font-serif text-base">Prioritized findings</h3>
        </div>
        <p className="mt-1 text-sm text-muted-foreground">
          Management-table view adapted from 21st.dev: ranked by risk, CVSS, EPSS, and fix data.
        </p>
      </div>
      <Badge variant={count ? 'danger' : 'success'}>
        {count ? `${count} open` : 'clear'}
      </Badge>
    </div>
  );
}
