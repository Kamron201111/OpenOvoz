# OpenBudget Ovozlar Bot

Telegram bot — openbudget.uz saytidan ovozlarni ko'rish, Excel yuklab olish va qidirish.

## Imkoniyatlar

- 📥 **Excel yuklab olish** — 10, 20, 30, 50, 100 yoki barcha ovozlarni
- 🔍 **Qidirish** — telefon raqamning oxirgi raqamlari bo'yicha ovoz topish
- ✅ **Chiroyli formatlangan** Excel fayl (rang-barang, sarlavha, jami)

## O'rnatish

```bash
pip install -r requirements.txt
```

## Sozlash

`bot.py` faylida yoki environment variable sifatida:

```bash
export BOT_TOKEN="123456:ABC-your-token-here"
```

Yoki `bot.py` ichida to'g'ridan-to'g'ri:
```python
BOT_TOKEN = "123456:ABC-your-token-here"
```

## Ishga tushirish

```bash
python bot.py
```

## Railway / Koyeb uchun

### railway.json
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": { "builder": "NIXPACKS" },
  "deploy": { "startCommand": "python bot.py", "restartPolicyType": "ON_FAILURE" }
}
```

### Environment variables (Railway/Koyeb):
```
BOT_TOKEN = sizning_bot_tokeningiz
```

## Bot buyruqlari

| Buyruq | Vazifasi |
|--------|---------|
| `/start` | Bosh menyu |
| `/download` | Excel yuklab olish |
| `/search` | Ovoz qidirish |
| `/help` | Yordam |
| `/cancel` | Jarayonni bekor qilish |

## API haqida

Bot openbudget.uz API dan foydalanadi:

- `POST /api/v1/scrape_votes` — `{"initiative_id": "UUID"}` yuboradi
- `GET /api/v1/votes?initiative_id=UUID` — zaxira so'rov

Response formati:
```json
{
  "success": true,
  "data": {
    "votes": [
      {"phoneNumber": "**-*63-33-35", "voteDate": "2026-03-12 22:54"},
      ...
    ]
  }
}
```

## Telefon raqam qidirish

Saytda raqamlar yashirilgan: `**-*63-33-35`
Qidiruvda **oxirgi 4-11 raqamni** kiritish kifoya.
Masalan: `633335` → `**-*63-33-35` topiladi.
