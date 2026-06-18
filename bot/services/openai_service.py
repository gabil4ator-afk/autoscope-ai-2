
from openai import OpenAI
from PIL import Image
import base64
from io import BytesIO
from bot.config import GITHUB_TOKEN

TEXT_PROMPT = """
Ты — опытный эксперт по автоподбору со стажем 10 лет и глубоким пониманием рынка б/у автомобилей (Авито, Авто.ру, Дром).

🏆 Оценка: X/100
📈 Надёжность: X%
⚠️ Риск: X%
💰 Торг: X%

🚩 Красные флаги:
• ...
🏁 Вердикт: ...
"""

VISION_PROMPT = """
Ты — эксперт по автоподбору и криминалист автомобильных объявлений.
Анализируй все полученные скриншоты как одно объявление.
Если это не объявление автомобиля:
Ошибка: На изображении не обнаружено объявление о продаже автомобиля.
"""

client = OpenAI(
    api_key=GITHUB_TOKEN,
    base_url="https://models.github.ai/inference"
)

async def analyze_text(text:str):
    r = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {"role":"system","content":TEXT_PROMPT},
            {"role":"user","content":text}
        ],
        max_tokens=700
    )
    return r.choices[0].message.content

def _img_to_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

async def analyze_images(image_paths):
    content = [{"type":"text","text":VISION_PROMPT}]
    for p in image_paths:
        content.append({
            "type":"image_url",
            "image_url":{"url":f"data:image/jpeg;base64,{_img_to_b64(p)}"}
        })

    r = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{"role":"user","content":content}],
        max_tokens=700
    )
    return r.choices[0].message.content
