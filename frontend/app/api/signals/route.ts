import { NextRequest, NextResponse } from "next/server";
import { getPool, SignalEvent } from "@/lib/db";

const RANGE_MS: Record<string, number> = {
  "24h": 24 * 60 * 60 * 1000,
  "7d": 7 * 24 * 60 * 60 * 1000,
  "30d": 30 * 24 * 60 * 60 * 1000,
};

export async function GET(req: NextRequest) {
  const assetClass = req.nextUrl.searchParams.get("asset_class") || "all";
  const signalName = req.nextUrl.searchParams.get("signal_name") || "all";
  const direction = req.nextUrl.searchParams.get("direction") || "all";
  const range = req.nextUrl.searchParams.get("range") || "7d";
  const limit = Math.min(Number(req.nextUrl.searchParams.get("limit")) || 200, 500);

  const clauses: string[] = [];
  const params: (string | number)[] = [];
  let idx = 1;

  if (assetClass !== "all") {
    clauses.push(`asset_class = $${idx++}`);
    params.push(assetClass);
  }
  if (signalName !== "all") {
    clauses.push(`signal_name = $${idx++}`);
    params.push(signalName);
  }
  if (direction !== "all") {
    clauses.push(`direction = $${idx++}`);
    params.push(direction);
  }
  if (range !== "all" && RANGE_MS[range]) {
    const since = new Date(Date.now() - RANGE_MS[range]).toISOString();
    clauses.push(`triggered_at >= $${idx++}`);
    params.push(since);
  }

  const where = clauses.length ? `WHERE ${clauses.join(" AND ")}` : "";
  params.push(limit);

  try {
    const pool = getPool();
    const result = await pool.query<SignalEvent>(
      `SELECT id, asset_class, symbol, signal_name, direction, z_score, price, triggered_at
       FROM signal_events
       ${where}
       ORDER BY triggered_at DESC
       LIMIT $${idx}`,
      params
    );
    return NextResponse.json({ signals: result.rows });
  } catch (err) {
    return NextResponse.json(
      { signals: [], error: "No data yet — run the backend scheduler at least once." },
      { status: 200 }
    );
  }
}