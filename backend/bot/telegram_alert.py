"""
Sends a Telegram message when a new, un-alerted signal event exists in the DB.

Setup: message @BotFather on Telegram to create a bot and get TELEGRAM_BOT_TOKEN.
Message @userinfobot to get your own numeric TELEGRAM_CHAT_ID. Put both in .env.
"""
import asyncio

from telegram import Bot

from backend.config import settings
from backend.db.models import SessionLocal, SignalEvent


def format_message(event: SignalEvent) -> str:
    arrow = "↑" if event.direction == "up" else "↓"
    return (
        f"{arrow} {event.symbol} ({event.asset_class})\n"
        f"Signal: {event.signal_name}\n"
        f"z-score: {event.z_score:.2f}\n"
        f"Price: {event.price}\n"
        f"Triggered: {event.triggered_at:%Y-%m-%d %H:%M UTC}"
    )


async def send_pending_alerts():
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        print("Telegram not configured — set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env")
        return

    bot = Bot(token=settings.telegram_bot_token)
    session = SessionLocal()
    try:
        pending = session.query(SignalEvent).filter_by(alerted=0).all()
        for event in pending:
            await bot.send_message(chat_id=settings.telegram_chat_id, text=format_message(event))
            event.alerted = 1
        session.commit()
        if pending:
            print(f"Sent {len(pending)} alert(s).")
    finally:
        session.close()


if __name__ == "__main__":
    # quick manual check: python -m backend.bot.telegram_alert
    asyncio.run(send_pending_alerts())
