# quant-trader

Personal research pipeline: pull market data, compute statistical signals, backtest them,
and get alerted on Telegram when a signal fires. Frontend dashboard comes later, once the
backend proves a signal is worth watching.

## Why this structure

- `backend/data/` — fetches raw OHLCV data (crypto via CCXT to start; forex/stocks slot in later
  as their own fetcher modules with the same interface).
- `backend/signals/` — turns raw data into a statistical signal (a number/score), decoupled
  from any single asset class or exchange.
- `backend/backtest/` — replays a signal against historical data honestly: no lookahead,
  fees and slippage included, so the result means something.
- `backend/db/` — SQLAlchemy models. Signals get written here; nothing else reads live data
  directly, which is what will let a frontend or a bot serve multiple users later.
- `backend/bot/` — Telegram alert on new signal rows.
- `backend/scheduler.py` — the loop: fetch → compute → store → alert, on a cadence.

## Setup

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env   # fill in your keys
```

## Run once (manual test)

```bash
python -m backend.scheduler --once
```

## Run continuously (VPS)

```bash
python -m backend.scheduler
```
Or better: run it under a process manager (systemd, supervisord, or Docker) so it restarts
on crash and starts on boot.

## Before you trust any signal

1. Backtest on data the model never saw during design (out-of-sample split).
2. Check performance survives realistic fees/slippage — see `backend/backtest/engine.py`.
3. Paper trade (log what you *would* have done) for weeks before real capital.
4. Only then wire up real order execution — this scaffold stops at alerting, deliberately.
   Adding live order placement is a separate, higher-stakes step.

## Roadmap

- [x] Crypto data fetcher (CCXT)
- [x] Example signal (z-scored return momentum)
- [x] Backtest engine with fees
- [x] DB models
- [x] Telegram alerting
- [ ] Forex fetcher module
- [ ] Stocks fetcher module
- [ ] Next.js frontend (reads from the same DB)
- [ ] Paper-trading tracker
- [ ] Live execution (only after a real track record)
