from google import genai
from PIL import Image
from bot.config import GEMINI_API_KEY

TEXT_PROMPT = '''Ты — опытный эксперт по автоподбору со стажем 10 лет и глубоким пониманием рынка б/у автомобилей.
Риск + Надёжность должны давать 100%.
Если есть серьёзные вложения, оценка не выше 65/100.
Ответ строго:
🏆 Оценка
📈 Надёжность
⚠️ Риск
💰 Торг
🚩 Красные флаги
🏁 Вердикт'''

VISION_PROMPT = '''Ты — эксперт по автоподбору и криминалист автомобильных объявлений.
Считай данные со скриншотов как одно объявление.
Если это не объявление автомобиля:
Ошибка: На изображении не обнаружено объявление о продаже автомобиля.
Риск + Надёжность = 100%.'''

client = genai.Client(api_key=GEMINI_API_KEY)

async def analyze_text(text:str):
    r = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{TEXT_PROMPT}\n\n{text}"
    )
    return r.text

async def analyze_images(image_paths):
    imgs=[Image.open(p) for p in image_paths]
    r = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=imgs + [VISION_PROMPT]
    )
    return r.text
