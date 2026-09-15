import type { SignalEvent } from "@/lib/db";

function formatTime(iso: string) {
  return new Date(iso).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function Card({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="rounded border border-hairline bg-panel/60 px-4 py-3.5">
      <p className="text-xs text-ash">{label}</p>
      <p className="mt-1 font-mono text-xl text-paper">{value}</p>
      {sub && <p className="mt-0.5 text-xs text-ash">{sub}</p>}
    </div>
  );
}

export default function StatCards({ signals }: { signals: SignalEvent[] }) {
  const total = signals.length;
  const upCount = signals.filter((s) => s.direction === "up").length;
  const downCount = total - upCount;
  const mostRecent = signals[0]?.triggered_at;

  return (
    <div className="mb-6 grid grid-cols-2 gap-3 md:grid-cols-4">
      <Card label="Signals in view" value={String(total)} />
      <Card label="Up" value={String(upCount)} />
      <Card label="Down" value={String(downCount)} />
      <Card label="Most recent" value={mostRecent ? formatTime(mostRecent) : "—"} />
    </div>
  );
}