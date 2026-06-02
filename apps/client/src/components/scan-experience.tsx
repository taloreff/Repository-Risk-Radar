'use client';

import { RiskDashboard } from '@/components/risk-dashboard';
import { InfiniteGridBackground } from '@/components/ui/the-infinite-grid';
import { ScanHeader } from '@/features/scan-experience/components/ScanHeader';
import { ScanHeroCard } from '@/features/scan-experience/components/ScanHeroCard';
import { ScannerContractCard } from '@/features/scan-experience/components/ScannerContractCard';
import { useRepoScan } from '@/features/scan-results/hooks/useRepoScan';

export function ScanExperience() {
  const scanState = useRepoScan();

  return (
    <main className="relative min-h-screen overflow-hidden px-4 py-6 sm:px-6 lg:px-8">
      <InfiniteGridBackground />
      <div className="relative z-10 mx-auto flex w-full max-w-[1600px] flex-col gap-6">
        <ScanHeader />
        <section className="grid gap-6 lg:grid-cols-[minmax(0,0.95fr)_minmax(360px,0.45fr)]">
          <ScanHeroCard
            error={scanState.error}
            examples={scanState.examples}
            loading={scanState.loading}
            repoUrl={scanState.repoUrl}
            scan={scanState.scan}
            useAi={scanState.useAi}
            onLoadDemo={scanState.loadDemo}
            onRepoUrlChange={scanState.setRepoUrl}
            onScan={scanState.scanRepo}
            onUseAiChange={scanState.setUseAi}
          />
          <ScannerContractCard />
        </section>
        {scanState.scan ? <RiskDashboard scan={scanState.scan} /> : null}
      </div>
    </main>
  );
}
