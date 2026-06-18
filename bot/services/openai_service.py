from openai import AsyncOpenAI
from bot.config import OPENAI_API_KEY
import base64

TEXT_PROMPT = '''Ты — опытный эксперт по автоподбору со стажем 10 лет и глубоким пониманием рынка б/у автомобилей. Соблюдай: Риск+Надёжность=100. Если есть серьёзные вложения, оценка не выше 65. Выдавай строго шаблон: Оценка, Надёжность, Риск, Торг, Красные флаги, Вердикт.'''

VISION_PROMPT = '''Ты — эксперт по автоподбору и криминалист автомобильных объявлений. Считай данные со скриншота. Если это не объявление, ответь ровно: Ошибка: На изображении не обнаружено объявление о продаже автомобиля. Риск+Надёжность=100.'''

client=AsyncOpenAI(api_key=OPENAI_API_KEY,base_url="https://openrouter.ai/api/v1")

async def analyze_text(text):
    r=await client.chat.completions.create(model="google/gemini-2.5-flash",messages=[{"role":"system","content":TEXT_PROMPT},{"role":"user","content":text}],max_tokens=700)
    return r.choices[0].message.content

async def analyze_images(image_paths):
    content=[{"type":"text","text":"Проанализируй все изображения как одно объявление"}]
    for p in image_paths:
        with open(p,"rb") as f:
            b64=base64.b64encode(f.read()).decode()
        content.append({"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}})
    try:
        r=await client.chat.completions.create(model="openai/gpt-4o-mini",messages=[{"role":"system","content":VISION_PROMPT},{"role":"user","content":content}],max_tokens=700)
        return r.choices[0].message.content
    except Exception:
        return "Не удалось считать текст со скриншота, пожалуйста, пришлите описание текстом"
