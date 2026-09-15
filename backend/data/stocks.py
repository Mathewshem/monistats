"""
Fetches OHLCV candles for stocks via yfinance \u2014 same library and reasoning
as backend.data.forex, just a plain ticker instead of a '=X' currency pair.
"""
import pandas as pd
import yfinance as yf


def fetch_ohlcv(symbol: str, interval: str = "60m", period: str = "5d") -> pd.DataFrame:
    """
    symbol: a plain stock ticker, e.g. 'AAPL', 'MSFT'.
    interval / period: see backend.data.forex.fetch_ohlcv \u2014 same defaults,
        same reasoning.

    Note: stock data only updates during that exchange's trading hours, so
    outside market hours (evenings, weekends, holidays) the most recent bar
    just won't be very recent \u2014 that's expected, not a bug.

    Returns the same open/high/low/close/volume shape as the crypto and
    forex fetchers.
    """
    raw = yf.Ticker(symbol).history(period=period, interval=interval)
    if raw.empty:
        raise ValueError(f"No data returned for {symbol} \u2014 check the ticker is correct and markets are open.")

    df = raw.rename(
        columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"}
    )[["open", "high", "low", "close", "volume"]]
    df.index = pd.to_datetime(df.index, utc=True)
    df.index.name = "timestamp"
    return df


if __name__ == "__main__":
    # quick manual check: python -m backend.data.stocks
    from backend.config import settings

    for symbol in settings.stock_symbols:
        try:
            df = fetch_ohlcv(symbol, interval="60m", period="5d")
            print(f"\n{symbol}:\n{df.tail(5)}")
        except Exception as e:
            print(f"{symbol}: failed to fetch \u2014 {e}")
