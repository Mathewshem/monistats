"use client";

import { useEffect, useState } from "react";
import type { SignalEvent } from "@/lib/db";

const ASSET_CLASSES = [
  { key: "crypto", label: "Crypto" },
  { key: "forex", label: "Forex" },
  { key: "stocks", label: "Stocks" },
] as const;

function formatTime(iso: string) {
  const d = new Date(iso);
  return d.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function Dashboard() {
  const [active, setActive] = useState<(typeof ASSET_CLASSES)[number]["key"]>("crypto");
  const [signals, setSignals] = useState<SignalEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetch(`/api/signals?asset_class=${active}`)
      .then((res) => res.json())
      .then((data) => {
        if (cancelled) return;
        setSignals(data.signals ?? []);
        setError(data.error ?? null);
      })
      .catch(() => {
        if (!cancelled) setError("Couldn't reach the signals API.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [active]);

  return (
    <main className="mx-auto max-w-4xl px-6 py-12">
      <header className="mb-10 flex items-baseline justify-between border-b border-hairline pb-6">
        <div>
          <h1 className="font-mono text-xl font-medium tracking-tight text-paper">monistats</h1>
          <p className="mt-1 text-sm text-ash">Live statistical signals, updated hourly.</p>
        </div>
      </header>

      <nav className="mb-8 flex gap-6 border-b border-hairline">
        {ASSET_CLASSES.map((ac) => (
          <button
            key={ac.key}
            onClick={() => setActive(ac.key)}
            className={`pb-3 text-sm font-medium transition-colors ${
              active === ac.key
                ? "border-b-2 border-up text-paper"
                : "border-b-2 border-transparent text-ash hover:text-paper"
            }`}
          >
            {ac.label}
          </button>
        ))}
      </nav>

      {loading && <p className="text-sm text-ash">Loading signals…</p>}

      {!loading && signals.length === 0 && (
        <div className="rounded border border-hairline bg-panel/40 px-5 py-6">
          <p className="text-sm text-paper">
            No {ASSET_CLASSES.find((a) => a.key === active)?.label.toLowerCase()} signals yet.
          </p>
          <p className="mt-1 text-sm text-ash">
            {error ?? "The backend hasn't reported anything for this asset class yet."}
          </p>
        </div>
      )}

      {!loading && signals.length > 0 && (
        <div className="overflow-hidden rounded border border-hairline">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-hairline bg-panel/60 text-ash">
                <th className="px-4 py-2.5 font-medium">Symbol</th>
                <th className="px-4 py-2.5 font-medium">Signal</th>
                <th className="px-4 py-2.5 font-medium">Direction</th>
                <th className="px-4 py-2.5 font-medium text-right font-mono">z-score</th>
                <th className="px-4 py-2.5 font-medium text-right font-mono">Price</th>
                <th className="px-4 py-2.5 font-medium text-right">Triggered</th>
              </tr>
            </thead>
            <tbody>
              {signals.map((s) => (
                <tr key={s.id} className="border-b border-hairline/60 last:border-0 hover:bg-panel/40">
                  <td className="px-4 py-3 font-mono text-paper">{s.symbol}</td>
                  <td className="px-4 py-3 text-ash">{s.signal_name}</td>
                  <td className="px-4 py-3">
                    <span className={s.direction === "up" ? "text-up" : "text-down"}>
                      {s.direction === "up" ? "▲ up" : "▼ down"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right font-mono text-paper">
                    {s.z_score.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-right font-mono text-paper">
                    {s.price.toLocaleString(undefined, { maximumFractionDigits: 4 })}
                  </td>
                  <td className="px-4 py-3 text-right text-ash">{formatTime(s.triggered_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
