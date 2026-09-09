"""
DB models. Everything downstream (frontend, Telegram bot) reads from these tables
instead of recomputing signals live — this is what makes it possible to add a
frontend, or more users, later without rearchitecting the backend.
"""
from datetime import datetime, timezone

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.config import settings

Base = declarative_base()


class SignalEvent(Base):
    __tablename__ = "signal_events"

    id = Column(Integer, primary_key=True)
    asset_class = Column(String, nullable=False)   # 'crypto' | 'forex' | 'stocks'
    symbol = Column(String, nullable=False)
    signal_name = Column(String, nullable=False)    # e.g. 'momentum_zscore'
    direction = Column(String, nullable=False)       # 'up' | 'down'
    z_score = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    triggered_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    alerted = Column(Integer, default=0)  # 0/1 flag so the bot doesn't double-alert


engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    init_db()
    print(f"Initialized DB at {settings.database_url}")
