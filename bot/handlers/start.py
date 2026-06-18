from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot.services.stats_service import register_user

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message):
    register_user(message.from_user.id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Отправить текст", callback_data="txt")],
        [InlineKeyboardButton(text="📸 Отправить скриншоты", callback_data="img")]
    ])
    await message.answer("🚗 AI Auto Check PRO", reply_markup=kb)
