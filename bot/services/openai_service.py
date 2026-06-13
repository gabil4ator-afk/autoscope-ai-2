from openai import AsyncOpenAI
from bot.config import OPENAI_API_KEY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = '''
Ты автомобильный аналитик.
Верни:
🚨 Риск перекупа
🚗 Живая машина
⚖️ Скрытые риски
🛡 Безопасность покупки
💸 Потенциал торга
🚩 Красные флаги
📋 Что спросить у продавца
💬 Текст для торга
🏁 Итоговая оценка
'''

async def analyze_text(text: str):
    response = await client.responses.create(
        model="gpt-5.5",
        input=[
            {"role":"system","content":SYSTEM_PROMPT},
            {"role":"user","content":text}
        ]
    )
    return response.output_text
