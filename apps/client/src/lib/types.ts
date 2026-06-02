export type CveEnrichment = {
  cve_id: string;
  cvss_score?: number | null;
  severity?: string | null;
  epss_score?: number | null;
  epss_percentile?: number | null;
  epss_date?: string | null;
  cwe_ids: string[];
  cisa_known_exploited: boolean;
  cisa_due_date?: string | null;
  published?: string | null;
  last_modified?: string | null;
  references: string[];
};

export type Dependency = {
  name: string;
  ecosystem: 'npm' | 'PyPI';
  source_file: string;
  version_constraint?: string | null;
  resolved_version?: string | null;
  dependency_type: 'direct' | 'dev' | 'optional' | 'unknown';
  display_version?: string;
};

export type Vulnerability = {
  id: string;
  summary?: string | null;
  details?: string | null;
  aliases: string[];
  published?: string | null;
  modified?: string | null;
  fixed_versions: string[];
  references: Array<{ type?: string | null; url: string }>;
};

export type Finding = {
  dependency: Dependency;
  vulnerability: Vulnerability;
  cves: CveEnrichment[];
  risk_score: number;
  risk_level: 'critical' | 'high' | 'medium' | 'low';
  reasons: string[];
  fix_available: boolean;
  fixed_versions: string[];
  highest_cvss?: number | null;
  highest_epss?: number | null;
  highest_severity?: string | null;
};

export type ScanStats = {
  dependencies_with_resolved_versions: number;
  dependencies_without_resolved_versions: number;
  osv_queries: number;
  osv_vulnerabilities: number;
  cves_enriched: number;
  epss_enriched: number;
};

export type ScanNarrative = {
  executive_summary: string;
  technical_summary: string;
  remediation_plan: string[];
  questions: string[];
  ai_generated: boolean;
};

export type ReleaseGateTicket = {
  title: string;
  description: string;
  acceptance_criteria: string[];
  evidence: string[];
};

export type ReleaseGateExplanation = {
  executive_summary: string;
  technical_summary: string;
  release_decision_explanation: string;
  top_required_actions: string[];
  safe_fix_plan: string[];
  what_would_make_this_pass: string[];
  developer_ticket: ReleaseGateTicket;
  questions_for_developer: string[];
  ai_generated: boolean;
};

export type ReleaseGate = {
  decision: 'PASS' | 'WARN' | 'BLOCK';
  confidence: 'high' | 'medium' | 'low';
  risk_score: number;
  blocking_reasons: string[];
  warning_reasons: string[];
  required_actions: string[];
  evidence: string[];
  unknowns: string[];
  pass_conditions: string[];
  developer_ticket: ReleaseGateTicket;
  explanation?: ReleaseGateExplanation | null;
};

export type ScanResult = {
  repo: {
    owner: string;
    name: string;
    full_name: string;
    html_url: string;
    default_branch: string;
    description?: string | null;
  };
  scanned_ref: string;
  manifests: string[];
  dependencies: Dependency[];
  findings: Finding[];
  stats: ScanStats;
  narrative?: ScanNarrative | null;
  release_gate?: ReleaseGate | null;
  generated_at: string;
  server_cache?: {
    hit: boolean;
    ttl_seconds: number;
  };
};
