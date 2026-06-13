import asyncio
from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN
from bot.handlers.start import router as start_router
from bot.handlers.analyze import router as analyze_router

async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(start_router)
    dp.include_router(analyze_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
