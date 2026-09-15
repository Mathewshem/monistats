"""
Mean reversion signal: price relative to its own rolling mean, in units of
rolling standard deviation (this is the same math as Bollinger Bands).

Opposite logic to momentum_zscore: instead of betting a strong move continues,
this bets an overextended move partially reverts. Worth backtesting both side
by side on the same data \u2014 they tend to win in different market conditions
(mean reversion does better in choppy/sideways markets, momentum in trending
ones), so watching which one is actually working right now is itself a useful
signal about the current regime.
"""
import pandas as pd


def compute(df: pd.DataFrame, window: int = 20, n_std: float = 2.0) -> pd.DataFrame:
    """
    df: OHLCV DataFrame with a 'close' column.
    window: bars used for the rolling mean/std (20 bars of 1h data = ~1 day).
    n_std: how many standard deviations define the bands.

    Adds: rolling_mean, rolling_std, upper_band, lower_band, band_z
    (band_z is how many std-devs price currently sits from its rolling mean —
    positive means price is above the mean/potentially overextended up,
    negative means below/potentially overextended down).
    """
    out = df.copy()
    out["rolling_mean"] = out["close"].rolling(window).mean()
    out["rolling_std"] = out["close"].rolling(window).std()
    out["upper_band"] = out["rolling_mean"] + n_std * out["rolling_std"]
    out["lower_band"] = out["rolling_mean"] - n_std * out["rolling_std"]
    out["band_z"] = (out["close"] - out["rolling_mean"]) / out["rolling_std"]
    return out


def latest_signal(df: pd.DataFrame, z_threshold: float = 2.0) -> dict | None:
    """
    Fires when price is z_threshold standard deviations from its rolling mean.
    direction 'down' means price is far ABOVE the mean (expect reversion down);
    'up' means price is far BELOW the mean (expect reversion up). This is
    intentionally the inverse framing from momentum_zscore's direction, since
    the trade idea itself is inverted.
    """
    scored = compute(df)
    last = scored.iloc[-1]
    if pd.isna(last["band_z"]):
        return None
    if abs(last["band_z"]) < z_threshold:
        return None
    return {
        "timestamp": scored.index[-1],
        "close": float(last["close"]),
        "rolling_mean": float(last["rolling_mean"]),
        "z_score": float(last["band_z"]),
        "direction": "down" if last["band_z"] > 0 else "up",
    }
