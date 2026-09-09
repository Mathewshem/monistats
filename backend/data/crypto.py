"""
Fetches OHLCV (open/high/low/close/volume) candles for crypto symbols via CCXT.
CCXT gives one interface across Coinbase, Kraken, Binance, etc. — swap EXCHANGE_ID
in .env to point at a different exchange without touching this code.
"""
import ccxt
import pandas as pd

from backend.config import settings


def get_exchange() -> ccxt.Exchange:
    exchange_class = getattr(ccxt, settings.exchange_id)
    return exchange_class(
        {
            "apiKey": settings.exchange_api_key or None,
            "secret": settings.exchange_api_secret or None,
            "enableRateLimit": True,
        }
    )


def fetch_ohlcv(symbol: str, timeframe: str = "1h", limit: int = 500) -> pd.DataFrame:
    """
    Returns a DataFrame indexed by UTC timestamp with columns:
    open, high, low, close, volume
    """
    exchange = get_exchange()
    raw = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df = df.set_index("timestamp")
    return df


if __name__ == "__main__":
    # quick manual check: python -m backend.data.crypto
    for symbol in settings.symbols:
        try:
            df = fetch_ohlcv(symbol, timeframe="1h", limit=5)
            print(f"\n{symbol}:\n{df}")
        except Exception as e:
            print(f"{symbol}: failed to fetch — {e}")
