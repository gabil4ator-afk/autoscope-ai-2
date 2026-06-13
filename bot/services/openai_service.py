from openai import AsyncOpenAI
from bot.config import OPENAI_API_KEY
import base64

client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

async def analyze_text(text:str):
    response = await client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=[{"role":"user","content":text}],
        max_tokens=700
    )
    return response.choices[0].message.content

async def analyze_images(image_paths):
    content = [{
        "type":"text",
        "text":'''Проанализируй скриншоты объявления автомобиля.
Верни только:

🏆 Рейтинг: XX/100
📈 Надёжность: XX%
⚠️ Риск: XX%
🤝 Честность продавца: XX%
💰 Потенциал торга: XX%

🚩 Красные флаги
📋 Вопросы продавцу
🏁 Вердикт'''
    }]

    for path in image_paths:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        content.append({
            "type":"image_url",
            "image_url":{"url":f"data:image/jpeg;base64,{b64}"}
        })

    response = await client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=[{"role":"user","content":content}],
        max_tokens=700
    )
    return response.choices[0].message.content
