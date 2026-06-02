import type {
  CveEnrichment,
  Finding,
  ReleaseGate,
  ReleaseGateTicket,
  ScanResult
} from '@/lib/types';

export type { CveEnrichment, Finding, ReleaseGate, ReleaseGateTicket, ScanResult };

export type RiskVariant = 'danger' | 'warning' | 'default' | 'secondary' | 'success';

export type ExploitabilityPoint = {
  name: string;
  advisory: string;
  risk: number;
  level: Finding['risk_level'];
  cvss: number;
  epss: number;
};
