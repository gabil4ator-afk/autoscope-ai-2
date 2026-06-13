from aiogram import Router, F
from aiogram.types import Message
from bot.services.openai_service import analyze_text

router = Router()

@router.message(F.photo)
async def photo_handler(message: Message):
    await message.answer(
        "📸 Скриншот получен. В этой версии выполняется базовая обработка. Для полного OCR подключите Gemini Vision или GPT-4o."
    )

@router.message(F.text)
async def analyze_handler(message: Message):
    msg = await message.answer("🔍 Анализирую объявление...")

    prompt = f"""
Проанализируй объявление автомобиля.

Верни:
🏆 Общий рейтинг: X/100
📈 Надёжность: X%
⚠️ Риск проблем: X%
🤝 Вероятность честного продавца: X%
💰 Потенциал торга: X%

Затем:
- Плюсы
- Минусы
- Красные флаги
- Вопросы продавцу
- Итог

Объявление:
{message.text}
"""
    result = await analyze_text(prompt)
    await msg.edit_text(result)
