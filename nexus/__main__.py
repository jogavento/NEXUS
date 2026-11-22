import asyncio
import logging
from .bot import NexusBot
from .config import Settings

async def run():
    settings = Settings.load()
    settings.prepare()
    logging.basicConfig(level=getattr(logging,settings.log_level,logging.INFO),
                        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    async with NexusBot(settings) as bot:
        await bot.start(settings.token)

def main():
    asyncio.run(run())

if __name__ == "__main__":
    main()
