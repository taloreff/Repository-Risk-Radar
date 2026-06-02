import type {
  CveEnrichment,
  ExploitabilityPoint,
  Finding,
  ReleaseGateTicket,
  ScanResult
} from '../types/scan.types';

export function scanCoverage(scan: ScanResult) {
  return scan.dependencies.length === 0
    ? 0
    : (scan.stats.osv_queries / scan.dependencies.length) * 100;
}

export function buildExploitabilityPoints(findings: Finding[]): ExploitabilityPoint[] {
  return findings.slice(0, 18).map((finding) => ({
    name: finding.dependency.name,
    advisory: finding.vulnerability.id,
    risk: finding.risk_score,
    level: finding.risk_level,
    cvss: highestCvss(finding) ?? 0,
    epss: (highestEpss(finding) ?? 0) * 100
  }));
}

export function highestCvss(finding: Finding) {
  const scores = finding.cves
    .map((cve) => cve.cvss_score)
    .filter((score): score is number => typeof score === 'number');
  return scores.length ? Math.max(...scores) : null;
}

export function highestEpss(finding: Finding) {
  const scores = finding.cves
    .map((cve) => cve.epss_score)
    .filter((score): score is number => typeof score === 'number');
  return scores.length ? Math.max(...scores) : null;
}

export function uniqueCves(findings: Finding[]): CveEnrichment[] {
  const byId = new Map<string, CveEnrichment>();
  findings.flatMap((finding) => finding.cves).forEach((cve) => byId.set(cve.cve_id, cve));
  return Array.from(byId.values());
}

export function formatTicket(ticket: ReleaseGateTicket) {
  return [
    `Title: ${ticket.title}`,
    '',
    'Body:',
    ticket.description,
    '',
    'Acceptance criteria:',
    ...ticket.acceptance_criteria.map((item) => `- ${item}`),
    '',
    'Evidence:',
    ...ticket.evidence.map((item) => `- ${item}`)
  ].join('\n');
}

export function nvdCveUrl(cveId: string) {
  return `https://nvd.nist.gov/vuln/detail/${encodeURIComponent(cveId)}`;
}
