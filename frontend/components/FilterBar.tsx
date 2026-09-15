"use client";

import { DIRECTIONS, RANGES, SIGNAL_TYPES } from "@/lib/constants";

export type Filters = {
  signal_name: string;
  direction: string;
  range: string;
};

function Select({
  value,
  onChange,
  options,
}: {
  value: string;
  onChange: (v: string) => void;
  options: readonly { key: string; label: string }[];
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="rounded border border-hairline bg-ink px-3 py-1.5 text-sm text-paper focus:border-accent focus:outline-none"
    >
      {options.map((o) => (
        <option key={o.key} value={o.key}>
          {o.label}
        </option>
      ))}
    </select>
  );
}

export default function FilterBar({
  filters,
  setFilters,
}: {
  filters: Filters;
  setFilters: (f: Filters) => void;
}) {
  return (
    <div className="mb-6 flex flex-wrap gap-3">
      <Select
        value={filters.signal_name}
        onChange={(v) => setFilters({ ...filters, signal_name: v })}
        options={SIGNAL_TYPES}
      />
      <Select
        value={filters.direction}
        onChange={(v) => setFilters({ ...filters, direction: v })}
        options={DIRECTIONS}
      />
      <Select
        value={filters.range}
        onChange={(v) => setFilters({ ...filters, range: v })}
        options={RANGES}
      />
    </div>
  );
}