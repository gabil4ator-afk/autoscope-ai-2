from aiogram import Router, F
from aiogram.types import Message
from bot.services.openai_service import analyze_text

router = Router()

@router.message(F.text)
async def analyze_handler(message: Message):
    msg = await message.answer("🔍 Анализирую объявление...")
    result = await analyze_text(message.text)
    await msg.edit_text(result)
