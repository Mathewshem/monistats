"""
Fetches OHLCV candles for forex pairs via yfinance \u2014 no API key, no signup,
no daily request cap (unlike Alpha Vantage's free tier, which was cut to just
25 requests/day and can't realistically support hourly checks across symbols).

yfinance pulls from Yahoo Finance, using the same '=X' ticker suffix Yahoo
uses for currency pairs, e.g. 'EURUSD=X', 'GBPUSD=X'.
"""
import pandas as pd
import yfinance as yf


def fetch_ohlcv(symbol: str, interval: str = "60m", period: str = "5d") -> pd.DataFrame:
    """
    symbol: a Yahoo Finance forex ticker, e.g. 'EURUSD=X'.
    interval: yfinance interval string ('60m' \u2248 the '1h' used elsewhere in this project).
    period: how much history to pull each call ('5d' is plenty for a rolling
        z-score with a ~1 week lookback window at hourly bars).

    Returns a DataFrame indexed by UTC timestamp with columns:
    open, high, low, close, volume \u2014 same shape as backend.data.crypto.fetch_ohlcv,
    so the existing signal modules work unchanged.
    """
    raw = yf.Ticker(symbol).history(period=period, interval=interval)
    if raw.empty:
        raise ValueError(f"No data returned for {symbol} \u2014 check the ticker format (e.g. 'EURUSD=X').")

    df = raw.rename(
        columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"}
    )[["open", "high", "low", "close", "volume"]]
    df.index = pd.to_datetime(df.index, utc=True)
    df.index.name = "timestamp"
    return df


if __name__ == "__main__":
    # quick manual check: python -m backend.data.forex
    from backend.config import settings

    for symbol in settings.forex_symbols:
        try:
            df = fetch_ohlcv(symbol, interval="60m", period="5d")
            print(f"\n{symbol}:\n{df.tail(5)}")
        except Exception as e:
            print(f"{symbol}: failed to fetch \u2014 {e}")
