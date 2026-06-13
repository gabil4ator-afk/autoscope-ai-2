
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.services.stats_service import get_stats

router = Router()

@router.message(Command("stats"))
async def stats_cmd(message: Message):
    users,texts,imgs = get_stats()
    await message.answer(
        f"📊 Статистика бота\n\n"
        f"👥 Пользователей: {users}\n"
        f"📝 Анализов текста: {texts}\n"
        f"📸 Анализов фото: {imgs}"
    )
