export function RepoExamples({
  examples,
  onLoadDemo,
  onSelectRepo
}: {
  examples: string[];
  onLoadDemo: () => void;
  onSelectRepo: (repoUrl: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      <button
        type="button"
        onClick={onLoadDemo}
        className="rounded-md border border-primary/40 px-2 py-1 text-xs text-primary transition hover:bg-primary/10"
      >
        Load demo
      </button>
      {examples.map((example) => (
        <button
          key={example}
          type="button"
          onClick={() => onSelectRepo(example)}
          className="rounded-md border px-2 py-1 text-xs text-muted-foreground transition hover:bg-muted hover:text-foreground"
        >
          {new URL(example).pathname.split('/').slice(1, 3).join('/')}
        </button>
      ))}
    </div>
  );
}
