"""
Minimal, honest backtest engine.

Two things kill most retail backtests: lookahead bias (using information you
wouldn't have had yet) and ignoring costs (fees + slippage). This engine:

- Only ever acts on a z-score computed from bars *up to and including* the
  current bar — no future data leaks in, because signals.compute() uses
  .rolling() and .pct_change(), which are backward-looking by construction.
- Subtracts a fee on every trade and applies a simple slippage haircut, so
  the equity curve reflects something closer to what you'd actually get filled at.
"""
import pandas as pd

from backend.signals.momentum_zscore import compute


def run_backtest(
    df: pd.DataFrame,
    z_threshold: float = 2.0,
    fee_bps: float = 10,      # 10 basis points = 0.10% per trade, adjust to your exchange
    slippage_bps: float = 5,  # extra haircut for market impact / spread
) -> pd.DataFrame:
    """
    Simple long/flat strategy: go long when z_score > threshold, flat otherwise.
    (Deliberately simple — add short positions, position sizing, or multi-asset
    logic once you trust the basic loop.)

    Returns a DataFrame with columns: position, strategy_return, equity_curve.
    """
    scored = compute(df)
    cost_per_trade = (fee_bps + slippage_bps) / 10_000

    scored["position"] = (scored["z_score"] > z_threshold).astype(int)
    scored["trade"] = scored["position"].diff().abs().fillna(0)

    scored["asset_return"] = scored["close"].pct_change()
    # position is decided on bar t using info through bar t, applied to bar t+1's return —
    # shift(1) here is what prevents the lookahead bias described above.
    scored["strategy_return"] = (
        scored["position"].shift(1).fillna(0) * scored["asset_return"]
        - scored["trade"] * cost_per_trade
    )
    scored["equity_curve"] = (1 + scored["strategy_return"]).cumprod()

    return scored


def summarize(result: pd.DataFrame) -> dict:
    total_return = result["equity_curve"].iloc[-1] - 1
    n_trades = int(result["trade"].sum())
    buy_hold_return = result["close"].iloc[-1] / result["close"].iloc[0] - 1
    daily_like = result["strategy_return"].dropna()
    sharpe_proxy = (
        (daily_like.mean() / daily_like.std()) * (len(daily_like) ** 0.5)
        if daily_like.std() and daily_like.std() > 0
        else float("nan")
    )
    return {
        "total_return_pct": round(total_return * 100, 2),
        "buy_hold_return_pct": round(buy_hold_return * 100, 2),
        "n_trades": n_trades,
        "sharpe_proxy": round(sharpe_proxy, 2),
    }


if __name__ == "__main__":
    # quick manual check: python -m backend.backtest.engine
    from backend.data.crypto import fetch_ohlcv
    from backend.config import settings

    for symbol in settings.symbols:
        df = fetch_ohlcv(symbol, timeframe="1h", limit=1000)
        result = run_backtest(df)
        print(symbol, summarize(result))
