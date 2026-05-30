import subprocess

subprocess.run(
    ["python", "-m", "playwright", "install", "chromium"],
    check=False
)
import os

ADMIN_ID = int(os.getenv("ADMIN_ID"))
import os

from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
import asyncio
import sqlite3
import requests

from bs4 import BeautifulSoup

from playwright.async_api import async_playwright
from playwright_stealth import stealth

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton
)



# ======================================================
# TOKENS
# ======================================================


# ======================================================
# TELEGRAM
# ======================================================

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()

# ======================================================
# OPENROUTER / DEEPSEEK
# ======================================================

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# ======================================================
# DATABASE
# ======================================================

conn = sqlite3.connect("autoscope.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (

    user_id INTEGER PRIMARY KEY,

    username TEXT,

    checks INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")

conn.commit()

# ======================================================
# DATABASE FUNCTIONS
# ======================================================

def add_user(user_id, username):

    cursor.execute(
        """
        INSERT OR IGNORE INTO users
        (user_id, username)
        VALUES (?, ?)
        """,
        (user_id, username)
    )

    conn.commit()

def add_check(user_id):

    cursor.execute(
        """
        UPDATE users
        SET checks = checks + 1
        WHERE user_id = ?
        """,
        (user_id,)
    )

    conn.commit()

def get_stats():

    cursor.execute("SELECT COUNT(*) FROM users")

    users = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(checks) FROM users")

    checks = cursor.fetchone()[0]

    if checks is None:
        checks = 0

    return users, checks

# ======================================================
# KEYBOARD
# ======================================================

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚗 Проверка модели")],
        [KeyboardButton(text="📋 Анализ объявления")],
        [KeyboardButton(text="🔍 VIN анализ")],
        [KeyboardButton(text="💰 Анализ расходов")]
    ],
    resize_keyboard=True
)

# ======================================================
# PROMPTS
# ======================================================

MODEL_PROMPT = """
Ты профессиональный автоподборщик.

Отвечай как реальный эксперт.

Не используй markdown.
Не используй звездочки.

Пиши:
- кратко
- четко
- профессионально

Формат:

🚗 Авто:
...

⚠️ Что важно:
• ...
• ...

🔧 Слабые места:
• ...
• ...

✅ Плюсы:
• ...
• ...

💰 Расходы:
...

📉 Ликвидность:
...

📌 Итог:
...
"""

LISTING_PROMPT = """
Ты профессиональный автоподборщик.

Разбирай объявление как настоящий эксперт.

Анализируй:
- скрученный пробег
- перекупов
- скрытые ДТП
- проблемные моторы
- проблемные коробки
- коммерческую эксплуатацию
- сомнительное описание
- подозрительно низкую цену

Не используй markdown.
Не используй звездочки.

Пиши:
- кратко
- красиво
- уверенно
- как подборщик

Формат:

📋 Объявление

🚗 Авто:
...

💰 Рынок:
...

⚠️ Что смущает:
• ...
• ...

🔍 Что проверить:
• ...
• ...

🛠 Возможные вложения:
• ...
• ...

📉 Риск:
Низкий / Средний / Высокий

📌 Вердикт:
...
"""

VIN_PROMPT = """
Ты эксперт по VIN проверкам.

Не используй markdown.

Формат:

🔍 VIN

⚠️ Риски:
• ...

🔧 Проверить:
• ...

📌 Итог:
...
"""

SERVICE_PROMPT = """
Ты профессиональный автоподборщик.

Оцени стоимость содержания автомобиля.

Не используй markdown.

Формат:

💰 Расходы:
...

⛽ Топливо:
...

🔧 Обслуживание:
...

⚠️ Частые поломки:
• ...
• ...

📌 Итог:
...
"""

# ======================================================
# START
# ======================================================

@dp.message(CommandStart())
async def start(message: Message):

    add_user(
        message.from_user.id,
        message.from_user.username
    )

    text = """
🚗 AutoScope AI

Профессиональный AI автоподборщик

Что умеет бот:

• Анализ объявлений
• Проверка VIN
• Анализ рисков
• Анализ расходов
• Поиск слабых мест

Поддерживаются:
• Auto.ru
• Avito
• Drom

Отправьте:
• модель автомобиля
• VIN номер
• ссылку на объявление
"""

    await message.answer(
        text,
        reply_markup=keyboard
    )

# ======================================================
# STATS
# ======================================================

@dp.message(Command("stats"))
async def stats(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    users, checks = get_stats()

    await message.answer(
        f"👥 Пользователей: {users}\n"
        f"📋 Проверок: {checks}"
    )

# ======================================================
# AI
# ======================================================

async def ask_ai(prompt):

    try:

        response = client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:

        print(e)

        return "❌ AI временно недоступен."

# ======================================================
# MARKET PRICE
# ======================================================

def get_market_price(query):

    try:

        search_url = f"https://auto.drom.ru/?q={query}"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            search_url,
            headers=headers,
            timeout=10
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        prices = []

        for span in soup.find_all("span"):

            text = span.get_text()

            text = text.replace("₽", "")
            text = text.replace(" ", "")

            if text.isdigit():

                value = int(text)

                if 300000 < value < 50000000:
                    prices.append(value)

        if not prices:
            return None

        avg_price = sum(prices[:10]) // len(prices[:10])

        return avg_price

    except:

        return None

# ======================================================
# VIN
# ======================================================

def decode_vin(vin):

    try:

        url = (
            f"https://vpic.nhtsa.dot.gov/api/vehicles/"
            f"DecodeVin/{vin}?format=json"
        )

        response = requests.get(
            url,
            timeout=10
        )

        data = response.json()

        results = data["Results"]

        info = {}

        for item in results:

            variable = item.get("Variable")

            value = item.get("Value")

            if variable and value:
                info[variable] = value

        return {
            "make": info.get("Make"),
            "model": info.get("Model"),
            "year": info.get("Model Year")
        }

    except:

        return None

# ======================================================
# PARSER
# ======================================================

async def parse_listing(url):

    try:

        async with async_playwright() as p:

            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-extensions",
                    "--disable-background-networking",
                    "--disable-sync",
                    "--disable-default-apps"
                ]
            )

            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36"
                ),
                viewport={
                    "width": 1280,
                    "height": 720
                },
                locale="ru-RU"
            )

            page = await context.new_page()

            print("OPENING:", url)

            await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=15000
            )

            await page.wait_for_timeout(3000)

            print("STATUS:", await page.evaluate("document.readyState"))
            print("URL:", page.url)
            print("TITLE:", await page.title())

            html = await page.content()

            print("HTML LENGTH:", len(html))

            await browser.close()

        html_lower = html.lower()

        blocked_words = [
            "captcha",
            "cloudflare",
            "verify you are human",
            "access denied",
            "подозрительная активность",
            "автоматические запросы"
        ]

        for word in blocked_words:

            if word in html_lower:

                print("BLOCKED:", word)

                return None

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        for tag in soup([
            "script",
            "style",
            "noscript",
            "svg"
        ]):
            tag.decompose()

        text = soup.get_text(
            " ",
            strip=True
        )

        text = " ".join(text.split())

        print("TEXT LENGTH:", len(text))

        if len(text) < 300:

            title = ""

            if soup.title:
                title = soup.title.text.strip()

            print("USING TITLE")

            return title

        return text[:15000]

    except Exception as e:

        print("PARSER ERROR:", e)

        return None
# ======================================================
# MAIN
# ======================================================

@dp.message()
async def analyze(message: Message):

    user_text = message.text.strip()

    add_user(
        message.from_user.id,
        message.from_user.username
    )

    await bot.send_chat_action(
        message.chat.id,
        "typing"
    )

    try:

        # ==================================================
        # BUTTONS
        # ==================================================

        if user_text == "🚗 Проверка модели":

            await message.answer(
                "🚗 Введите модель автомобиля."
            )

            return

        if user_text == "📋 Анализ объявления":

            await message.answer(
                "📋 Отправьте ссылку или текст объявления."
            )

            return

        if user_text == "🔍 VIN анализ":

            await message.answer(
                "🔍 Отправьте VIN номер."
            )

            return

        if user_text == "💰 Анализ расходов":

            await message.answer(
                "💰 Введите модель автомобиля."
            )

            return

        # ==================================================
        # LINK ANALYSIS
        # ==================================================

        if (
            "http://" in user_text
            or "https://" in user_text
        ):

            add_check(message.from_user.id)

            listing_text = await parse_listing(
                user_text
            )

            if not listing_text:

                await message.answer(
                    "❌ Не удалось прочитать объявление.\n"
                    "Сайт временно блокирует парсер."
                )

                return

            prompt = f"""
{LISTING_PROMPT}

Текст объявления:

{listing_text}
"""

            answer = await ask_ai(prompt)

            await message.answer(answer)

            return

        # ==================================================
        # VIN ANALYSIS
        # ==================================================

        cleaned_text = user_text.replace(
            " ",
            ""
        ).upper()

        if (
            len(cleaned_text) == 17
            and cleaned_text.isalnum()
            and any(char.isdigit() for char in cleaned_text)
        ):

            add_check(message.from_user.id)

            vin_data = decode_vin(
                cleaned_text
            )

            prompt = f"""
{VIN_PROMPT}

VIN:
{cleaned_text}

Данные:
{vin_data}
"""

            answer = await ask_ai(prompt)

            await message.answer(answer)

            return

        # ==================================================
        # SERVICE ANALYSIS
        # ==================================================

        lower_text = user_text.lower()

        if (
            "расход" in lower_text
            or "обслуживание" in lower_text
            or "содержание" in lower_text
        ):

            add_check(message.from_user.id)

            prompt = f"""
{SERVICE_PROMPT}

Автомобиль:
{user_text}
"""

            answer = await ask_ai(prompt)

            await message.answer(answer)

            return

        # ==================================================
        # MODEL ANALYSIS
        # ==================================================

        add_check(message.from_user.id)

        market_price = get_market_price(
            user_text
        )

        prompt = f"""
{MODEL_PROMPT}

Автомобиль:
{user_text}

Средняя цена рынка:
{market_price}
"""

        answer = await ask_ai(prompt)

        await message.answer(answer)

    except Exception as e:

        print(e)

        await message.answer(
            "❌ Ошибка анализа."
        )

# ======================================================
# RUN
# ======================================================

async def main():

    print("✅ AutoScope AI запущен")

    await dp.start_polling(bot)

if __name__ == "__main__":

    asyncio.run(main())
