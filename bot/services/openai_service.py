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

Верни ответ кратко и по делу.

Формат:

🚨 Риск перекупа
🚗 Живая машина
⚖️ Скрытые риски
🛡 Безопасность покупки
💸 Потенциал торга
🚩 Красные флаги
📋 Что спросить у продавца
💬 Текст для торга
🏁 Итоговая оценка

Не выдавай предположения за факты.
Используй формулировки: есть признаки, вероятно, рекомендуется проверить.
"""

async def analyze_text(text: str):
    try:
        response = await client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0.4,
            max_tokens=700
        )

        return response.choices[0].message.content

    except Exception as e:
        error_text = str(e)

        if "402" in error_text:
            return "Ошибка OpenRouter: недостаточно средств на балансе (402). Пополните баланс или используйте более дешёвую модель."

        if "401" in error_text:
            return "Ошибка OpenRouter: неверный API-ключ (401). Проверьте OPENAI_API_KEY."

        return f"Ошибка анализа: {error_text}"
