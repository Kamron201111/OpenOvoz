import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
OPENBUDGET_API_URL: str = os.getenv("OPENBUDGET_API_URL", "https://api.openbudget.uz/votes")
API_TOKEN: str = os.getenv("API_TOKEN", "")  # agar kerak bo'lsa

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN .env faylida yo'q!")
