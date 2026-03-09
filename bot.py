import asyncio
import logging

from pyrogram import Client

import config
from database import create_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Create the shared Client instance first, then import handlers so they
# can call register(app) with this object.
# ---------------------------------------------------------------------------
app = Client(
    name="FileSearchBot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
)

# Import after app is defined — handlers register themselves via register(app)
from handlers import register_all  # noqa: E402
register_all(app)


async def main():
    missing = []
    if not config.API_ID:
        missing.append("API_ID")
    if not config.API_HASH:
        missing.append("API_HASH")
    if not config.BOT_TOKEN:
        missing.append("BOT_TOKEN")
    if not config.DB_CHANNEL_ID:
        missing.append("DB_CHANNEL_ID")

    if missing:
        logger.critical("Missing required env vars: %s", ", ".join(missing))
        return

    await create_indexes()
    logger.info("MongoDB indexes ensured.")

    async with app:
        me = await app.get_me()
        logger.info("Bot started as @%s (id=%s)", me.username, me.id)
        logger.info("DB channel   : %s", config.DB_CHANNEL_ID)
        logger.info(
            "Force join   : %s",
            f"@{config.FORCE_JOIN_CHANNEL}" if config.FORCE_JOIN_CHANNEL else "disabled",
        )
        logger.info("Admins       : %s", config.ADMINS or "none configured")
        await asyncio.sleep(float("inf"))


if __name__ == "__main__":
    asyncio.run(main())
