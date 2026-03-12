import asyncio
import logging
import re
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_TOKEN
from database import init_db, load_votes_from_api, check_phone

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()


def clean_phone(raw: str) -> str:
    """
    Foydalanuvchi kiritgan raqamdan faqat raqamlarni oladi,
    keyin birinchi 3 ta raqamni olib tashlaydi.
    Misol: '91 690 1966' -> '916901966' -> '6901966'
    """
    digits = re.sub(r'\D', '', raw)
    if len(digits) < 4:
        return ""
    return digits[3:]


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 Salom! Men OpenBudget ovozlarini tekshiruvchi botman.\n\n"
        "📱 Telefon raqamingizni yuboring.\n"
        "Misol: <code>91 690 1966</code> yoki <code>916901966</code>\n\n"
        "Bot raqamning boshidagi 3 ta raqamni olib tashlab bazada qidiradi.",
        parse_mode="HTML"
    )


@dp.message(Command("reload"))
async def cmd_reload(message: Message):
    await message.answer("🔄 Ovozlar yangilanmoqda...")
    count = await load_votes_from_api()
    if count is not None:
        await message.answer(f"✅ {count} ta ovoz yuklandi.")
    else:
        await message.answer("❌ API dan ma'lumot olishda xatolik yuz berdi.")


@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    from database import get_stats
    count = await get_stats()
    await message.answer(f"📊 Bazada jami: <b>{count}</b> ta ovoz mavjud.", parse_mode="HTML")


@dp.message(F.text)
async def handle_phone(message: Message):
    raw = message.text.strip()
    cleaned = clean_phone(raw)

    if not cleaned:
        await message.answer(
            "❗ Noto'g'ri format. Raqam kamida 4 xonali bo'lishi kerak.\n"
            "Misol: <code>91 690 1966</code>",
            parse_mode="HTML"
        )
        return

    result = await check_phone(cleaned)

    if result:
        voted_at = result.get("voted_at", "noma'lum vaqt")
        await message.answer(
            f"✅ <b>Topildi!</b>\n\n"
            f"📱 Raqam: <code>{cleaned}</code>\n"
            f"🕐 Ovoz berilgan vaqt: <b>{voted_at}</b>",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            f"❌ <b>Topilmadi.</b>\n\n"
            f"📱 <code>{cleaned}</code> raqami bazada mavjud emas.",
            parse_mode="HTML"
        )


async def scheduled_reload():
    logger.info("Scheduled reload: ovozlar yangilanmoqda...")
    count = await load_votes_from_api()
    if count is not None:
        logger.info(f"Scheduled reload: {count} ta ovoz yuklandi.")
    else:
        logger.error("Scheduled reload: API xatolik.")


async def on_startup():
    logger.info("Bot ishga tushdi. Ovozlar yuklanmoqda...")
    count = await load_votes_from_api()
    if count is not None:
        logger.info(f"Boshlang'ich yuklash: {count} ta ovoz.")
    else:
        logger.warning("Boshlang'ich yuklashda API xatolik — bot ishlashda davom etadi.")

    # Har kuni soat 03:00 da yangilanadi
    scheduler.add_job(scheduled_reload, "cron", hour=3, minute=0)
    scheduler.start()


async def main():
    await init_db()
    await on_startup()
    logger.info("Polling boshlanmoqda...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
