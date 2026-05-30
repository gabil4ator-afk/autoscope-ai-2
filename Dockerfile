FROM python:3.11-slim

WORKDIR /app

# Директория для БД и файлов

ENV DATA_DIR=/app/data

RUN mkdir -p /app/data && chmod 777 /app/data
RUN chown -R 1000:1000 /app/data || true

# Устанавливаем только нужные зависимости

RUN pip install --no-cache-dir 
aiogram 
requests 
aiohttp 
beautifulsoup4 
bs4 
openai 
python-dotenv 
fake-useragent 
lxml 
pyTelegramBotAPI

# Очистка кеша pip

RUN pip cache purge || true

# Копируем проект

COPY . .

# Entrypoint

RUN echo '#!/bin/sh' > /usr/local/bin/entrypoint.sh && 
echo 'set -e' >> /usr/local/bin/entrypoint.sh && 
echo 'mkdir -p /app/data' >> /usr/local/bin/entrypoint.sh && 
echo 'chmod 777 /app/data' >> /usr/local/bin/entrypoint.sh && 
echo 'exec "$@"' >> /usr/local/bin/entrypoint.sh && 
chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD ["python", "bot.py"]

