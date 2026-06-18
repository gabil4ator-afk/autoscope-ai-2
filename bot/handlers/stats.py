from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.services.stats_service import get_stats
from bot.config import ADMIN_ID

router = Router()

@router.message(Command("stats"))
async def stats_cmd(message: Message):
    if ADMIN_ID and message.from_user.id != ADMIN_ID:
        return
    users,texts,imgs = get_stats()
    await message.answer(
        f"📊 Статистика\n\n👥 Пользователей: {users}\n📝 Анализов текста: {texts}\n📸 Анализов фото: {imgs}"
    )
