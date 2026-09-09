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
from backend.data.crypto import fetch_ohlcv
from backend.signals.momentum_zscore import latest_signal
from backend.db.models import init_db, SessionLocal, SignalEvent
from backend.bot.telegram_alert import send_pending_alerts


def run_cycle():
    init_db()
    session = SessionLocal()
    try:
        for symbol in settings.symbols:
            try:
                df = fetch_ohlcv(symbol, timeframe="1h", limit=500)
            except Exception as e:
                print(f"[{symbol}] fetch failed: {e}")
                continue

            signal = latest_signal(df)
            if signal is None:
                print(f"[{symbol}] no signal (threshold not cleared)")
                continue

            # avoid writing a duplicate event for the same bar
            already_exists = (
                session.query(SignalEvent)
                .filter_by(symbol=symbol, triggered_at=signal["timestamp"])
                .first()
            )
            if already_exists:
                continue

            event = SignalEvent(
                asset_class="crypto",
                symbol=symbol,
                signal_name="momentum_zscore",
                direction=signal["direction"],
                z_score=signal["z_score"],
                price=signal["close"],
                triggered_at=signal["timestamp"],
            )
            session.add(event)
            print(f"[{symbol}] new signal: {signal}")
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
