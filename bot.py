import os, re, json, asyncio, sqlite3
from openai import OpenAI
from carapis import VehiclesAPIClient
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
CARAPIS_KEY = os.getenv("CARAPIS_KEY")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not set")
if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY not set")
if not CARAPIS_KEY:
    raise RuntimeError("CARAPIS_KEY not set")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

carapis_client = VehiclesAPIClient(base_url="https://api.carapis.com", api_key=CARAPIS_KEY)

conn = sqlite3.connect("autoscope.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    checks INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

def add_user(user_id, username):
    cursor.execute(
        "INSERT OR IGNORE INTO users(user_id, username) VALUES(?, ?)",
        (user_id, username)
    )
    conn.commit()

def add_check(user_id):
    cursor.execute(
        "UPDATE users SET checks = checks + 1 WHERE user_id=?",
        (user_id,)
    )
    conn.commit()

def get_stats():
    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]
    cursor.execute("SELECT COALESCE(SUM(checks),0) FROM users")
    checks = cursor.fetchone()[0]
    return users, checks

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Анализ объявления")],
        [KeyboardButton(text="🔍 VIN анализ")],
        [KeyboardButton(text="🚗 Проверка модели")],
        [KeyboardButton(text="💰 Анализ расходов")]
    ],
    resize_keyboard=True
)

LISTING_PROMPT = """
Ты профессиональный автоэксперт.

Проанализируй JSON автомобиля.

Оцени:
1. Адекватность цены
2. Возможные риски
3. Вероятность перекупа
4. Реальность пробега
5. Что проверить перед покупкой
6. Ликвидность модели
7. Итоговая оценка от 1 до 10
"""

def extract_id(url: str):
    if not url:
        return None
    m = re.search(r"/(\d+)\.html(?:\?.*)?$", url)
    if m:
        return m.group(1)
    nums = re.findall(r"\d+", url)
    return nums[-1] if nums else None

async def ask_ai(prompt: str):
    try:
        result = client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )
        return result.choices[0].message.content
    except Exception as e:
        return f"Ошибка AI: {e}"

async def parse_listing(url: str):
    try:
        vehicle_id = extract_id(url)
        print(f"[CARAPIS] URL: {url}")
        print(f"[CARAPIS] ID: {vehicle_id}")
        if not vehicle_id:
            return None

        vehicle = await carapis_client.vehicles.get_async(vehicle_id)

        data = {
            "id": getattr(vehicle, "id", vehicle_id),
            "title": getattr(vehicle, "title", None),
            "brand": getattr(vehicle, "brand", None),
            "model": getattr(vehicle, "model", None),
            "year": getattr(vehicle, "year", None),
            "mileage": getattr(vehicle, "mileage", None),
            "market": getattr(vehicle, "market", None),
            "seller": getattr(vehicle, "seller", None),
            "location": getattr(vehicle, "location", None),
            "url": url
        }

        price = getattr(vehicle, "price", None)
        if price:
            data["price"] = {
                "amount": getattr(price, "amount", None),
                "formatted": getattr(price, "formatted", None),
                "currency": getattr(price, "currency", None)
            }

        return json.dumps(data, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"CARAPIS ERROR: {e!r}")
        return None

@dp.message(CommandStart())
async def start(message: Message):
    add_user(message.from_user.id, message.from_user.username)
    await message.answer("Пришлите ссылку Auto.ru/Drom, VIN или модель автомобиля.", reply_markup=keyboard)

@dp.message(Command("stats"))
async def stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    users, checks = get_stats()
    await message.answer(f"Пользователей: {users}\\nПроверок: {checks}")

@dp.message()
async def analyze(message: Message):
    text = (message.text or "").strip()
    add_user(message.from_user.id, message.from_user.username)

    if text.startswith("http"):
        add_check(message.from_user.id)
        vehicle_json = await parse_listing(text)
        if not vehicle_json:
            await message.answer("Не удалось обработать ссылку.")
            return

        report = await ask_ai(
            f"{LISTING_PROMPT}\\n\\nJSON:\\n{vehicle_json}"
        )
        await message.answer(report)
        return

    report = await ask_ai(f"Проанализируй автомобиль: {text}")
    await message.answer(report)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
