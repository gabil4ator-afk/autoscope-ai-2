from aiogram import Router, F
from aiogram.types import Message
from bot.services.openai_service import analyze_text, analyze_images
from pathlib import Path
from bot.services.stats_service import inc_text, inc_image
import asyncio

router = Router()

media_groups = {}

async def process_group(bot, chat_id, media_group_id):
    await asyncio.sleep(3)
    group = media_groups.pop(media_group_id, None)
    if not group:
        return

    image_paths = group["paths"]
    status = await bot.send_message(chat_id, "🔍 Анализирую объявление...")

    inc_image(chat_id)
    result = await analyze_images(image_paths)
    await status.edit_text(result)

@router.message(F.photo)
async def photo_handler(message: Message):
    media_group_id = message.media_group_id

    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)

    tmp = Path(f"/tmp/{photo.file_id}.jpg")
    await message.bot.download_file(file.file_path, destination=tmp)

    if media_group_id:
        if media_group_id not in media_groups:
            media_groups[media_group_id] = {
                "paths": [],
                "task": asyncio.create_task(
                    process_group(message.bot, message.chat.id, media_group_id)
                )
            }

        media_groups[media_group_id]["paths"].append(str(tmp))
    else:
        status = await message.answer("🔍 Анализирую...")
        inc_image(message.from_user.id)
        result = await analyze_images([str(tmp)])
        await status.edit_text(result)

@router.message(F.text)
async def analyze_handler(message: Message):
    status = await message.answer("🔍 Анализ...")
    inc_text(message.from_user.id)
    result = await analyze_text(message.text)
    await status.edit_text(result)
