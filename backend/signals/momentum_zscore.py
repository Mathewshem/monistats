"""
Example signal: z-scored momentum.

This is a STARTING POINT to show the pattern a signal module should follow, not a
strategy anyone should trust with real money as-is. Swap in your own hypothesis —
on-chain flow z-scores, funding-rate divergence, whatever you want to test — by
writing a new module with the same shape: takes OHLCV, returns a score + a rule.

The idea: compute rolling return, standardize it (z-score) against its own recent
history so the signal is comparable across assets with different volatility, then
apply an explicit numeric threshold — not a vibe — to decide if it's "signal-worthy".
"""
import pandas as pd


def compute(df: pd.DataFrame, lookback: int = 24, z_window: int = 168) -> pd.DataFrame:
    """
    df: OHLCV DataFrame from backend.data.crypto.fetch_ohlcv (or any fetcher with
        the same 'close' column).
    lookback: bars to compute momentum over (24 bars of 1h data = 1 day).
    z_window: bars used to compute the mean/std the z-score is measured against
        (168 bars of 1h data = 1 week).

    Returns the input df with two added columns: 'momentum' and 'z_score'.
    """
    out = df.copy()
    out["momentum"] = out["close"].pct_change(lookback)
    rolling_mean = out["momentum"].rolling(z_window).mean()
    rolling_std = out["momentum"].rolling(z_window).std()
    out["z_score"] = (out["momentum"] - rolling_mean) / rolling_std
    return out


def latest_signal(df: pd.DataFrame, z_threshold: float = 0.1) -> dict | None:
    """
    Looks at the most recent row and decides whether it clears the threshold.
    Returns None if there isn't enough history yet, or a dict describing the
    signal if the threshold is cleared. This is what gets written to the DB
    and what triggers an alert — the threshold is the actual "trading rule",
    make it explicit and back-test it before trusting it.
    """
    scored = compute(df)
    last = scored.iloc[-1]
    if pd.isna(last["z_score"]):
        return None
    if abs(last["z_score"]) < z_threshold:
        return None
    return {
        "timestamp": scored.index[-1],
        "close": float(last["close"]),
        "momentum": float(last["momentum"]),
        "z_score": float(last["z_score"]),
        "direction": "up" if last["z_score"] > 0 else "down",
    }
