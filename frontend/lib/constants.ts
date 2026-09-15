import { LayoutGrid, Coins, ArrowLeftRight, LineChart } from "lucide-react";

export const ASSET_CLASSES = [
  { key: "all", label: "All" as const, icon: LayoutGrid },
  { key: "crypto", label: "Crypto" as const, icon: Coins },
  { key: "forex", label: "Forex" as const, icon: ArrowLeftRight },
  { key: "stocks", label: "Stocks" as const, icon: LineChart },
] as const;

export type AssetClassKey = (typeof ASSET_CLASSES)[number]["key"];

export const SIGNAL_TYPES = [
  { key: "all", label: "All signals" },
  { key: "momentum_zscore", label: "Momentum" },
  { key: "mean_reversion", label: "Mean reversion" },
] as const;

export const DIRECTIONS = [
  { key: "all", label: "Any direction" },
  { key: "up", label: "Up" },
  { key: "down", label: "Down" },
] as const;

export const RANGES = [
  { key: "24h", label: "Last 24h" },
  { key: "7d", label: "Last 7 days" },
  { key: "30d", label: "Last 30 days" },
  { key: "all", label: "All time" },
] as const;