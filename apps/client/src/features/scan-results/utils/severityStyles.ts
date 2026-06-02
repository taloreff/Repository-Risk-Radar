import type { Finding, ReleaseGate, RiskVariant } from '../types/scan.types';

export function riskTone(level: Finding['risk_level']): RiskVariant {
  if (level === 'critical' || level === 'high') {
    return 'danger';
  }
  if (level === 'medium') {
    return 'warning';
  }
  return 'secondary';
}

export function riskColor(level: Finding['risk_level']) {
  if (level === 'critical') return '#fb5572';
  if (level === 'high') return '#f87171';
  if (level === 'medium') return '#f5b51b';
  return '#34d399';
}

export function releaseGateVariant(decision: ReleaseGate['decision']): RiskVariant {
  if (decision === 'BLOCK') return 'danger';
  if (decision === 'WARN') return 'warning';
  return 'success';
}

export function releaseGateFrame(decision: ReleaseGate['decision']) {
  if (decision === 'BLOCK') {
    return 'border-danger/45 shadow-danger/15';
  }
  if (decision === 'WARN') {
    return 'border-warning/45 shadow-warning/15';
  }
  return 'border-primary/45 shadow-primary/15';
}
