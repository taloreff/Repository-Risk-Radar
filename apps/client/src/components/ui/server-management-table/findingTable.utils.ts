import type { Finding } from '@/lib/types';

export function riskTone(level: Finding['risk_level']) {
  if (level === 'critical' || level === 'high') {
    return 'danger';
  }
  if (level === 'medium') {
    return 'warning';
  }
  return 'secondary';
}

export function riskGradient(level: Finding['risk_level']) {
  if (level === 'critical' || level === 'high') {
    return 'from-danger/14 to-transparent';
  }
  if (level === 'medium') {
    return 'from-warning/12 to-transparent';
  }
  return 'from-primary/10 to-transparent';
}

export function riskBarColor(level: Finding['risk_level']) {
  if (level === 'critical' || level === 'high') {
    return 'border-danger/50 bg-danger/70';
  }
  if (level === 'medium') {
    return 'border-warning/50 bg-warning/70';
  }
  return 'border-primary/50 bg-primary/70';
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
