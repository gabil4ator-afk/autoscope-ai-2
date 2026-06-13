from openai import AsyncOpenAI
from bot.config import OPENAI_API_KEY

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY не найден. Добавьте переменную окружения в Bothost.")

client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

SYSTEM_PROMPT = """
Ты автомобильный аналитик.

Верни отчет строго в формате:

🚨 Риск перекупа: XX%
🚗 Живая машина: XX/100
⚖️ Скрытые риски: XX%
🛡 Безопасность покупки: XX%
💸 Потенциал торга: XX%

🚩 Красные флаги
- список рисков

📋 Что спросить у продавца
- список вопросов

💬 Текст для торга

🏁 Итоговая оценка: X.X/10

Не выдавай предположения за факты.
Используй формулировки: есть признаки, вероятно, рекомендуется проверить.
"""

async def analyze_text(text: str):
    response = await client.chat.completions.create(
        model="anthropic/claude-sonnet-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        temperature=0.4
    )

    return response.choices[0].message.content
