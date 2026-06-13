from openai import AsyncOpenAI
from bot.config import OPENAI_API_KEY
import base64

SYSTEM_PROMPT = '''Ты — профессиональный эксперт по автоподбору.
Верни только:
🏆 Оценка: X/100
📈 Надёжность: X%
⚠️ Риск: X%
💰 Торг: X%

🚩 Красные флаги:
• пункт

🏁 Вердикт: 1-2 предложения.
'''

client = AsyncOpenAI(api_key=OPENAI_API_KEY, base_url='https://openrouter.ai/api/v1')

async def analyze_text(text:str):
    r = await client.chat.completions.create(
        model='google/gemini-2.5-flash',
        messages=[
            {'role':'system','content':SYSTEM_PROMPT},
            {'role':'user','content':text}
        ],
        max_tokens=500
    )
    return r.choices[0].message.content

async def analyze_images(image_paths):
    content=[{'type':'text','text':'Проанализируй все изображения как одно объявление'}]
    for p in image_paths:
        with open(p,'rb') as f:
            b64=base64.b64encode(f.read()).decode()
        content.append({'type':'image_url','image_url':{'url':f'data:image/jpeg;base64,{b64}'}})
    try:
        r = await client.chat.completions.create(
            model='openai/gpt-4o-mini',
            messages=[
                {'role':'system','content':SYSTEM_PROMPT},
                {'role':'user','content':content}
            ],
            max_tokens=500
        )
        return r.choices[0].message.content
    except Exception:
        return 'Не удалось считать текст со скриншота, пожалуйста, пришлите описание текстом'
