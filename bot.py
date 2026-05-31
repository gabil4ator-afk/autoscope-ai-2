import os, re, json, asyncio, sqlite3
from openai import OpenAI
from carapis import VehiclesAPIClient
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
CARAPIS_KEY = os.getenv("CARAPIS_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

ai_client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

car_client = VehiclesAPIClient(
    base_url="https://api.carapis.com",
    api_key=CARAPIS_KEY
)

def extract_id(url:str):
    m = re.search(r"(\d+)\.html", url)
    if m:
        return m.group(1)
    m = re.search(r"(\d{5,})", url)
    return m.group(1) if m else None

async def parse_listing(url:str):
    try:
        vehicle_id = extract_id(url)
        if not vehicle_id:
            return None

        vehicle = car_client.vehicles.get(vehicle_id)

        data = {
            "id": getattr(vehicle, "id", vehicle_id),
            "title": getattr(vehicle, "title", ""),
            "brand": getattr(vehicle, "brand", ""),
            "model": getattr(vehicle, "model", ""),
            "year": getattr(vehicle, "year", ""),
            "mileage": getattr(vehicle, "mileage", ""),
            "market": getattr(vehicle, "market", ""),
            "url": url
        }

        return json.dumps(data, ensure_ascii=False, indent=2)

    except Exception as e:
        print("CARAPIS ERROR:", repr(e))
        return None

async def ask_ai(car_json:str):
    try:
        resp = ai_client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[{
                "role":"user",
                "content":f"Проанализируй автомобиль и дай рекомендации:\\n{car_json}"
            }]
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Ошибка AI: {e}"

@dp.message(CommandStart())
async def start(msg:Message):
    await msg.answer("Отправьте ссылку Auto.ru или Drom")

@dp.message()
async def handle(msg:Message):
    text = (msg.text or "").strip()

    if text.startswith("http"):
        data = await parse_listing(text)

        if not data:
            await msg.answer("Не удалось обработать ссылку. Смотри логи CARAPIS ERROR.")
            return

        report = await ask_ai(data)
        await msg.answer(report)
        return

    await msg.answer("Пришлите ссылку на объявление")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
