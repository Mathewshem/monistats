"""
Backtest for mean_reversion.py. Same honest structure as backtest/engine.py
(fees, slippage, no lookahead via shift(1)) but the position logic is inverted:
go long when price is far BELOW its mean (expect bounce up), flat otherwise.
Short-side (fading overextended-up moves) is left out deliberately \u2014 add it
once the long-only version's logic is trusted.
"""
import pandas as pd

from backend.signals.mean_reversion import compute


def run_backtest(
    df: pd.DataFrame,
    z_threshold: float = 2.0,
    fee_bps: float = 10,
    slippage_bps: float = 5,
) -> pd.DataFrame:
    scored = compute(df)
    cost_per_trade = (fee_bps + slippage_bps) / 10_000

    # long when price is far below its rolling mean (band_z very negative)
    scored["position"] = (scored["band_z"] < -z_threshold).astype(int)
    scored["trade"] = scored["position"].diff().abs().fillna(0)

    scored["asset_return"] = scored["close"].pct_change()
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
    # quick manual check: python -m backend.backtest.mean_reversion_engine
    from backend.data.crypto import fetch_ohlcv
    from backend.config import settings

    for symbol in settings.symbols:
        df = fetch_ohlcv(symbol, timeframe="1h", limit=1000)
        result = run_backtest(df)
        print(symbol, summarize(result))
