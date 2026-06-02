import type { ScanResult } from '@/lib/types';

export function CacheNotice({ cache }: { cache: ScanResult['server_cache'] }) {
  if (!cache) {
    return null;
  }

  return (
    <p className="mx-auto max-w-2xl text-xs text-muted-foreground">
      {cache.hit
        ? `Served from server cache. Repeated scans reuse results for ${cache.ttl_seconds} seconds.`
        : `Fresh scan cached for ${cache.ttl_seconds} seconds to avoid GitHub API churn.`}
    </p>
  );
}
