from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

print("BOT_TOKEN loaded:", bool(BOT_TOKEN))
print("OPENAI_API_KEY loaded:", bool(OPENAI_API_KEY))
