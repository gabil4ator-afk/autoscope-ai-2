from aiogram import Router, F
from aiogram.types import Message
from bot.services.openai_service import analyze_text, analyze_images
from pathlib import Path

router = Router()

@router.message(F.photo)
async def photo_handler(message: Message):
    status = await message.answer("📸 Анализирую скриншот...")

    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)

    tmp = Path(f"/tmp/{photo.file_id}.jpg")
    await message.bot.download_file(file.file_path, destination=tmp)

    result = await analyze_images([str(tmp)])
    await status.edit_text(result)

@router.message(F.text)
async def analyze_handler(message: Message):
    status = await message.answer("🔍 Анализ...")
    result = await analyze_text(message.text)
    await status.edit_text(result)
