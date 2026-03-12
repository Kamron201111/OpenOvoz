import aiosqlite
import aiohttp
import logging
from typing import Optional
from config import OPENBUDGET_API_URL, API_TOKEN

logger = logging.getLogger(__name__)
DB_PATH = "votes.db"


async def init_db():
    """Bazani yaratadi."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT NOT NULL UNIQUE,
                voted_at TEXT
            )
        """)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_phone ON votes(phone)")
        await db.commit()
    logger.info("Baza tayyor.")


async def load_votes_from_api() -> Optional[int]:
    """
    OpenBudget API'dan barcha ovozlarni yuklab bazaga saqlaydi.
    Mavjud ma'lumotlarni tozalab yangi ma'lumot yozadi.
    """
    headers = {}
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"

    all_votes = []
    page = 1

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            while True:
                params = {"page": page, "limit": 1000}
                async with session.get(OPENBUDGET_API_URL, params=params, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                    if resp.status != 200:
                        logger.error(f"API xatolik: {resp.status}")
                        # Agar birinchi sahifada xatolik bo'lsa None qaytaradi
                        if page == 1:
                            return None
                        break

                    data = await resp.json()

                    # API javob formatiga moslash:
                    # {"results": [...], "next": ...} yoki {"data": [...]} yoki to'g'ridan list
                    if isinstance(data, list):
                        items = data
                        has_next = False
                    elif isinstance(data, dict):
                        items = data.get("results") or data.get("data") or data.get("votes") or []
                        has_next = bool(data.get("next"))
                    else:
                        items = []
                        has_next = False

                    if not items:
                        break

                    all_votes.extend(items)
                    logger.info(f"Sahifa {page}: {len(items)} ta ovoz olindi (jami: {len(all_votes)})")

                    if not has_next:
                        break
                    page += 1

    except aiohttp.ClientError as e:
        logger.error(f"API ulanish xatoligi: {e}")
        return None
    except Exception as e:
        logger.exception(f"Kutilmagan xatolik: {e}")
        return None

    if not all_votes:
        logger.warning("API bo'sh javob qaytardi.")
        return 0

    # Bazaga yozish
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("DELETE FROM votes")

            rows = []
            for item in all_votes:
                # API'dan kelgan maydon nomlarini moslashtirish
                # Mumkin nomlar: phone, phone_number, msisdn, number, mobile
                phone_raw = (
                    item.get("phone")
                    or item.get("phone_number")
                    or item.get("msisdn")
                    or item.get("number")
                    or item.get("mobile")
                    or ""
                )
                voted_at = (
                    item.get("voted_at")
                    or item.get("created_at")
                    or item.get("date")
                    or item.get("timestamp")
                    or "noma'lum"
                )

                if not phone_raw:
                    continue

                # Faqat raqamlarni qoldirish
                import re
                phone_digits = re.sub(r'\D', '', str(phone_raw))
                if not phone_digits:
                    continue

                rows.append((phone_digits, str(voted_at)))

            await db.executemany(
                "INSERT OR REPLACE INTO votes (phone, voted_at) VALUES (?, ?)",
                rows
            )
            await db.commit()

        logger.info(f"Bazaga {len(rows)} ta ovoz yozildi.")
        return len(rows)

    except Exception as e:
        logger.exception(f"Bazaga yozishda xatolik: {e}")
        return None


async def check_phone(cleaned_phone: str) -> Optional[dict]:
    """
    Tozalangan raqamni bazada qidiradi.
    Topilsa {'voted_at': '...'} qaytaradi, topilmasa None.
    """
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            # To'liq mos kelish
            async with db.execute(
                "SELECT phone, voted_at FROM votes WHERE phone LIKE ?",
                (f"%{cleaned_phone}",)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {"phone": row[0], "voted_at": row[1]}
    except Exception as e:
        logger.exception(f"check_phone xatolik: {e}")
    return None


async def get_stats() -> int:
    """Bazadagi jami ovozlar sonini qaytaradi."""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT COUNT(*) FROM votes") as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0
    except Exception:
        return 0
