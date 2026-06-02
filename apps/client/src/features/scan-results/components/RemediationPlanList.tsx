import { ListChecks } from 'lucide-react';

export function RemediationPlanList({ steps }: { steps: string[] }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <ListChecks className="h-4 w-4 text-primary" aria-hidden="true" />
        <h3 className="font-medium">Plan</h3>
      </div>
      {steps.length ? (
        <ol className="space-y-2 text-sm text-muted-foreground">
          {steps.slice(0, 5).map((item, index) => (
            <li key={item} className="flex gap-2">
              <span className="text-foreground">{index + 1}.</span>
              <span>{item}</span>
            </li>
          ))}
        </ol>
      ) : (
        <p className="text-sm text-muted-foreground">No remediation steps were needed.</p>
      )}
    </div>
  );
}
