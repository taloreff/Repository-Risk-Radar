import { FindingManagementTable } from '@/components/ui/server-management-table';

import type { Finding } from '../types/scan.types';

export function PrioritizedFindingsTable({ findings }: { findings: Finding[] }) {
  return <FindingManagementTable findings={findings} />;
}
