export function ReleaseGateInfoBlock({
  title,
  items,
  ordered = false
}: {
  title: string;
  items: string[];
  ordered?: boolean;
}) {
  const ListTag = ordered ? 'ol' : 'ul';
  return (
    <div className="rounded-lg border bg-background/50 p-4">
      <h3 className="text-base">{title}</h3>
      <ListTag className="mt-3 space-y-2 text-sm text-muted-foreground">
        {items.map((item, index) => (
          <li key={`${title}-${item}`} className="flex gap-2">
            <span className="font-mono text-primary">{ordered ? `${index + 1}.` : '-'}</span>
            <span>{item}</span>
          </li>
        ))}
      </ListTag>
    </div>
  );
}
