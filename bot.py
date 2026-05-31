import os, re, json, asyncio, sqlite3, requests
from openai import OpenAI
import carapis

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
CARAPIS_KEY = os.getenv("CARAPIS_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")
carapis_client = carapis.Client(api_key=CARAPIS_KEY)

conn = sqlite3.connect("autoscope.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users(
user_id INTEGER PRIMARY KEY,
username TEXT,
checks INTEGER DEFAULT 0,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
conn.commit()

def add_user(user_id, username):
    cursor.execute("INSERT OR IGNORE INTO users(user_id,username) VALUES(?,?)",(user_id,username))
    conn.commit()

def add_check(user_id):
    cursor.execute("UPDATE users SET checks=checks+1 WHERE user_id=?",(user_id,))
    conn.commit()

def get_stats():
    cursor.execute("SELECT COUNT(*) FROM users")
    users=cursor.fetchone()[0]
    cursor.execute("SELECT COALESCE(SUM(checks),0) FROM users")
    checks=cursor.fetchone()[0]
    return users,checks

keyboard = ReplyKeyboardMarkup(
keyboard=[[KeyboardButton(text="🚗 Проверка модели")],[KeyboardButton(text="📋 Анализ объявления")],[KeyboardButton(text="🔍 VIN анализ")],[KeyboardButton(text="💰 Анализ расходов")]],
resize_keyboard=True)

LISTING_PROMPT = """Ты профессиональный автоподборщик.
Тебе передан JSON автомобиля.
Оцени цену, риски, пробег, перекупа, ликвидность, слабые места и итоговую оценку 1-10.
Пиши профессионально и структурировано."""

MODEL_PROMPT="Проанализируй автомобиль как эксперт по автоподбору."
VIN_PROMPT="Проанализируй VIN и возможные риски."
SERVICE_PROMPT="Оцени стоимость содержания автомобиля."

def extract_id(url:str):
    patterns=[r'(\\d+)\\.html',r'/vehicle/(\\d+)',r'_(\\d+)$',r'(\\d{5,})']
    for p in patterns:
        m=re.search(p,url)
        if m:
            return m.group(1)
    return None

async def ask_ai(prompt):
    try:
        r=client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[{"role":"user","content":prompt}]
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"Ошибка AI: {e}"

def decode_vin(vin):
    try:
        url=f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"
        return requests.get(url,timeout=15).json()
    except:
        return None

async def parse_listing(url:str):
    vehicle_id = extract_id(url)
    if not vehicle_id:
        return None
    vehicle = carapis_client.get_vehicle(vehicle_id)

    car = {
        "id": getattr(vehicle,"id",vehicle_id),
        "title": getattr(vehicle,"title",None),
        "brand": getattr(vehicle,"brand",None),
        "model": getattr(vehicle,"model",None),
        "year": getattr(vehicle,"year",None),
        "mileage": getattr(vehicle,"mileage",None),
        "market": getattr(vehicle,"market",None),
        "seller": getattr(vehicle,"seller",None),
        "location": getattr(vehicle,"location",None),
        "url": url
    }

    price=getattr(vehicle,"price",None)
    if price:
        car["price"]={
            "amount": getattr(price,"amount",None),
            "formatted": getattr(price,"formatted",None),
            "currency": getattr(price,"currency",None)
        }

    return json.dumps(car,ensure_ascii=False,indent=2)

@dp.message(CommandStart())
async def start(message: Message):
    add_user(message.from_user.id,message.from_user.username)
    await message.answer("🚗 AutoScope AI готов к работе.\nПришлите ссылку Auto.ru/Drom, VIN или модель автомобиля.",reply_markup=keyboard)

@dp.message(Command("stats"))
async def stats(message: Message):
    if message.from_user.id!=ADMIN_ID:
        return
    users,checks=get_stats()
    await message.answer(f"👥 Пользователей: {users}\n📋 Проверок: {checks}")

@dp.message()
async def analyze(message: Message):
    text=message.text.strip()
    add_user(message.from_user.id,message.from_user.username)

    if text.startswith("http"):
        add_check(message.from_user.id)
        data=await parse_listing(text)
        if not data:
            await message.answer("Не удалось получить данные объявления.")
            return
        answer=await ask_ai(f"{LISTING_PROMPT}\n\nJSON:\n{data}")
        await message.answer(answer)
        return

    cleaned=text.replace(" ","").upper()
    if len(cleaned)==17 and cleaned.isalnum():
        add_check(message.from_user.id)
        answer=await ask_ai(f"{VIN_PROMPT}\n\n{decode_vin(cleaned)}")
        await message.answer(answer)
        return

    if any(x in text.lower() for x in ["расход","обслуживание","содержание"]):
        add_check(message.from_user.id)
        answer=await ask_ai(f"{SERVICE_PROMPT}\nАвто:{text}")
        await message.answer(answer)
        return

    add_check(message.from_user.id)
    answer=await ask_ai(f"{MODEL_PROMPT}\nАвтомобиль:{text}")
    await message.answer(answer)

async def main():
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())
