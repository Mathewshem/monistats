"use client";

import { useEffect, useState } from "react";
import { Menu } from "lucide-react";
import type { SignalEvent } from "@/lib/db";
import { ASSET_CLASSES, AssetClassKey } from "@/lib/constants";
import Sidebar from "./Sidebar";
import FilterBar, { Filters } from "./FilterBar";
import StatCards from "./StatCards";

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
  const [active, setActive] = useState<AssetClassKey>("all");
  const [desktopCollapsed, setDesktopCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [filters, setFilters] = useState<Filters>({
    signal_name: "all",
    direction: "all",
    range: "7d",
  });
  const [signals, setSignals] = useState<SignalEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    const params = new URLSearchParams({
      asset_class: active,
      signal_name: filters.signal_name,
      direction: filters.direction,
      range: filters.range,
    });
    fetch(`/api/signals?${params.toString()}`)
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
  }, [active, filters]);

  const activeLabel = ASSET_CLASSES.find((a) => a.key === active)?.label ?? "All";

  return (
    <div className="flex min-h-screen">
      <Sidebar
        active={active}
        onSelect={setActive}
        desktopCollapsed={desktopCollapsed}
        setDesktopCollapsed={setDesktopCollapsed}
        mobileOpen={mobileOpen}
        setMobileOpen={setMobileOpen}
      />

      <main className="min-w-0 flex-1 px-5 py-6 md:px-10 md:py-10">
        <header className="mb-8 flex items-center gap-3 border-b border-hairline pb-6">
          <button
            onClick={() => setMobileOpen(true)}
            className="rounded p-1.5 text-ash hover:bg-panel hover:text-paper md:hidden"
            aria-label="Open menu"
          >
            <Menu size={20} />
          </button>
          <div>
            <h1 className="font-mono text-lg font-medium tracking-tight text-paper md:text-xl">
              {activeLabel} signals
            </h1>
            <p className="mt-0.5 text-sm text-ash">Live statistical signals, updated hourly.</p>
          </div>
        </header>

        <StatCards signals={signals} />
        <FilterBar filters={filters} setFilters={setFilters} />

        {loading && <p className="text-sm text-ash">Loading signals…</p>}

        {!loading && signals.length === 0 && (
          <div className="rounded border border-hairline bg-panel/40 px-5 py-6">
            <p className="text-sm text-paper">No signals match these filters.</p>
            <p className="mt-1 text-sm text-ash">
              {error ?? "Try a wider time range, or check back after the backend's next run."}
            </p>
          </div>
        )}

        {!loading && signals.length > 0 && (
          <div className="overflow-x-auto rounded border border-hairline">
            <table className="w-full min-w-[640px] text-left text-sm">
              <thead>
                <tr className="border-b border-hairline bg-panel/60 text-ash">
                  <th className="px-4 py-2.5 font-medium">Symbol</th>
                  <th className="px-4 py-2.5 font-medium">Asset</th>
                  <th className="px-4 py-2.5 font-medium">Signal</th>
                  <th className="px-4 py-2.5 font-medium">Direction</th>
                  <th className="px-4 py-2.5 text-right font-mono font-medium">z-score</th>
                  <th className="px-4 py-2.5 text-right font-mono font-medium">Price</th>
                  <th className="px-4 py-2.5 text-right font-medium">Triggered</th>
                </tr>
              </thead>
              <tbody>
                {signals.map((s) => (
                  <tr
                    key={s.id}
                    className="border-b border-hairline/60 last:border-0 hover:bg-panel/40"
                  >
                    <td className="px-4 py-3 font-mono text-paper">{s.symbol}</td>
                    <td className="px-4 py-3 capitalize text-ash">{s.asset_class}</td>
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
    </div>
  );
}