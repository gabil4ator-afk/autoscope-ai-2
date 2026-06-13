from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Анализ объявления")],
            [KeyboardButton(text="📸 Анализ скриншотов")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "🚗 AI Auto Check PRO\n\nОтправьте текст объявления или скриншоты.",
        reply_markup=kb
    )
