import { NextRequest, NextResponse } from "next/server";
import { getPool, SignalEvent } from "@/lib/db";

export async function GET(req: NextRequest) {
  const assetClass = req.nextUrl.searchParams.get("asset_class") || "crypto";

  try {
    const pool = getPool();
    const result = await pool.query<SignalEvent>(
      `SELECT id, asset_class, symbol, signal_name, direction, z_score, price, triggered_at
       FROM signal_events
       WHERE asset_class = $1
       ORDER BY triggered_at DESC
       LIMIT 30`,
      [assetClass]
    );
    return NextResponse.json({ signals: result.rows });
  } catch (err) {
    // Table may not exist yet if the backend hasn't run against this DB.
    return NextResponse.json(
      { signals: [], error: "No data yet — run the backend scheduler at least once." },
      { status: 200 }
    );
  }
}
