'use client';

import { useState } from 'react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';

import type { ReleaseGate } from '../types/scan.types';
import { formatTicket } from '../utils/riskFormatters';
import { releaseGateFrame } from '../utils/severityStyles';
import { DeveloperTicketPanel } from './DeveloperTicketPanel';
import { ReleaseGateDecisionBadges } from './ReleaseGateDecisionBadges';
import { ReleaseGateInfoBlock } from './ReleaseGateInfoBlock';

export function ReleaseGateCard({ gate }: { gate: ReleaseGate }) {
  const [copied, setCopied] = useState(false);
  const reasons = gate.blocking_reasons.length ? gate.blocking_reasons : gate.warning_reasons;
  const actions = gate.explanation?.top_required_actions?.length
    ? gate.explanation.top_required_actions
    : gate.required_actions;
  const passConditions = gate.explanation?.what_would_make_this_pass?.length
    ? gate.explanation.what_would_make_this_pass
    : gate.pass_conditions;
  const ticket = gate.explanation?.developer_ticket ?? gate.developer_ticket;
  const ticketText = formatTicket(ticket);

  async function copyTicket() {
    await navigator.clipboard.writeText(ticketText);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }

  return (
    <Card className={cn('overflow-hidden', releaseGateFrame(gate.decision))}>
      <CardHeader className="border-b">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <CardDescription>AI Release Gate</CardDescription>
            <CardTitle className="mt-1 text-2xl">Can this repo ship today?</CardTitle>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
              {gate.explanation?.executive_summary ??
                'Deterministic release policy result generated from the scan findings.'}
            </p>
          </div>
          <ReleaseGateDecisionBadges gate={gate} />
        </div>
      </CardHeader>
      <CardContent className="grid gap-5 p-5 xl:grid-cols-[minmax(0,0.58fr)_minmax(360px,0.42fr)]">
        <div className="space-y-5">
          <ReleaseGateInfoBlock
            title="Why this decision?"
            items={reasons.length ? reasons : ['No blocking or warning thresholds fired.']}
          />
          <ReleaseGateInfoBlock title="Required before release" items={actions} ordered />
          <ReleaseGateInfoBlock title="What would make this pass?" items={passConditions} />
          {gate.unknowns.length ? (
            <ReleaseGateInfoBlock title="Unknowns" items={gate.unknowns} />
          ) : null}
        </div>
        <DeveloperTicketPanel
          ticketText={ticketText}
          copied={copied}
          aiGenerated={Boolean(gate.explanation?.ai_generated)}
          onCopy={copyTicket}
        />
      </CardContent>
    </Card>
  );
}
