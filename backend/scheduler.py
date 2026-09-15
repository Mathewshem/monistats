"""
The loop: fetch data -> compute signal -> store new events -> alert.

Run once for testing:      python -m backend.scheduler --once
Run continuously (VPS):    python -m backend.scheduler
"""
import argparse
import asyncio
from datetime import datetime, timezone

from apscheduler.schedulers.blocking import BlockingScheduler

from backend.config import settings
from backend.data import crypto, forex, stocks
from backend.signals import momentum_zscore, mean_reversion
from backend.db.models import init_db, SessionLocal, SignalEvent
from backend.bot.telegram_alert import send_pending_alerts

# each entry: (signal_name, module) — add more signals here as you build them
SIGNAL_MODULES = [
    ("momentum_zscore", momentum_zscore),
    ("mean_reversion", mean_reversion),
]

# each entry: (asset_class, symbol list, fetch function, fetch kwargs)
# adding a new asset class later means adding one line here, nothing else changes
ASSET_CLASSES = [
    ("crypto", settings.symbols, crypto.fetch_ohlcv, {"timeframe": "1h", "limit": 500}),
    ("forex", settings.forex_symbols, forex.fetch_ohlcv, {"interval": "60m", "period": "5d"}),
    ("stocks", settings.stock_symbols, stocks.fetch_ohlcv, {"interval": "60m", "period": "5d"}),
]


def run_cycle():
    init_db()
    session = SessionLocal()
    try:
        for asset_class, symbols, fetch_fn, fetch_kwargs in ASSET_CLASSES:
            for symbol in symbols:
                try:
                    df = fetch_fn(symbol, **fetch_kwargs)
                except Exception as e:
                    print(f"[{asset_class}/{symbol}] fetch failed: {e}")
                    continue

                for signal_name, module in SIGNAL_MODULES:
                    signal = module.latest_signal(df)
                    if signal is None:
                        print(f"[{asset_class}/{symbol}] {signal_name}: no signal (threshold not cleared)")
                        continue

                    # avoid writing a duplicate event for the same bar + signal
                    already_exists = (
                        session.query(SignalEvent)
                        .filter_by(symbol=symbol, signal_name=signal_name, triggered_at=signal["timestamp"])
                        .first()
                    )
                    if already_exists:
                        continue

                    event = SignalEvent(
                        asset_class=asset_class,
                        symbol=symbol,
                        signal_name=signal_name,
                        direction=signal["direction"],
                        z_score=signal["z_score"],
                        price=signal["close"],
                        triggered_at=signal["timestamp"],
                    )
                    session.add(event)
                    print(f"[{asset_class}/{symbol}] {signal_name}: new signal: {signal}")
        session.commit()
    finally:
        session.close()

    asyncio.run(send_pending_alerts())
    print(f"Cycle complete at {datetime.now(timezone.utc):%Y-%m-%d %H:%M:%S} UTC")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run a single cycle and exit")
    parser.add_argument(
        "--interval-minutes", type=int, default=60, help="Minutes between cycles when running continuously"
    )
    args = parser.parse_args()

    if args.once:
        run_cycle()
        return

    scheduler = BlockingScheduler()
    scheduler.add_job(run_cycle, "interval", minutes=args.interval_minutes, next_run_time=datetime.now())
    print(f"Starting scheduler, every {args.interval_minutes} min. Ctrl+C to stop.")
    scheduler.start()


if __name__ == "__main__":
    main()
