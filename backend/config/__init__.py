import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    exchange_id: str = os.getenv("EXCHANGE_ID", "coinbase")
    exchange_api_key: str = os.getenv("EXCHANGE_API_KEY", "")
    exchange_api_secret: str = os.getenv("EXCHANGE_API_SECRET", "")

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./quant_trader.db")

    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")

    symbols: list = field(
        default_factory=lambda: [
            s.strip() for s in os.getenv("SYMBOLS", "BTC/USDT,ETH/USDT").split(",") if s.strip()
        ]
    )
    forex_symbols: list = field(
        default_factory=lambda: [
            s.strip() for s in os.getenv("FOREX_SYMBOLS", "EURUSD=X,GBPUSD=X").split(",") if s.strip()
        ]
    )
    stock_symbols: list = field(
        default_factory=lambda: [
            s.strip() for s in os.getenv("STOCK_SYMBOLS", "AAPL,MSFT").split(",") if s.strip()
        ]
    )


settings = Settings()
