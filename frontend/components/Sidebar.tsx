"use client";

import { ChevronsLeft, ChevronsRight } from "lucide-react";
import { ASSET_CLASSES, AssetClassKey } from "@/lib/constants";

export default function Sidebar({
  active,
  onSelect,
  desktopCollapsed,
  setDesktopCollapsed,
  mobileOpen,
  setMobileOpen,
}: {
  active: AssetClassKey;
  onSelect: (key: AssetClassKey) => void;
  desktopCollapsed: boolean;
  setDesktopCollapsed: (v: boolean) => void;
  mobileOpen: boolean;
  setMobileOpen: (v: boolean) => void;
}) {
  return (
    <>
      {mobileOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 md:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 border-r border-hairline bg-panel transition-transform duration-200 md:static md:translate-x-0 ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        } ${desktopCollapsed ? "md:w-16" : "md:w-64"}`}
      >
        <div className="flex h-full flex-col">
          <div className="flex items-center justify-between border-b border-hairline px-4 py-4">
            <span
              className={`font-mono text-sm font-medium text-paper ${
                desktopCollapsed ? "md:hidden" : ""
              }`}
            >
              monistats
            </span>
            <button
              onClick={() => setDesktopCollapsed(!desktopCollapsed)}
              className="hidden rounded p-1 text-ash hover:bg-ink hover:text-paper md:block"
              aria-label="Toggle sidebar"
            >
              {desktopCollapsed ? <ChevronsRight size={16} /> : <ChevronsLeft size={16} />}
            </button>
          </div>

          <nav className="flex-1 space-y-1 p-3">
            {ASSET_CLASSES.map((ac) => {
              const Icon = ac.icon;
              const isActive = active === ac.key;
              return (
                <button
                  key={ac.key}
                  onClick={() => {
                    onSelect(ac.key);
                    setMobileOpen(false);
                  }}
                  className={`flex w-full items-center gap-3 rounded px-3 py-2 text-sm transition-colors ${
                    isActive
                      ? "bg-accent/15 text-accent"
                      : "text-ash hover:bg-ink hover:text-paper"
                  }`}
                >
                  <Icon size={17} className="shrink-0" />
                  <span className={desktopCollapsed ? "md:hidden" : ""}>{ac.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </aside>
    </>
  );
}