import { Pool } from "pg";

// A single shared pool, reused across requests in the same server process.
// DATABASE_URL is the same Postgres connection string the Python backend
// writes to — this file only ever reads from it.
let pool: Pool | undefined;

export function getPool(): Pool {
  if (!pool) {
    pool = new Pool({
      connectionString: process.env.DATABASE_URL,
      ssl: process.env.DATABASE_URL?.includes("sslmode=require")
        ? { rejectUnauthorized: false }
        : undefined,
    });
  }
  return pool;
}

export type SignalEvent = {
  id: number;
  asset_class: string;
  symbol: string;
  signal_name: string;
  direction: "up" | "down";
  z_score: number;
  price: number;
  triggered_at: string;
};
