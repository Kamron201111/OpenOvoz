# OpenBudget Ovoz Tekshiruvchi Bot

## Ishlash tartibi
1. Foydalanuvchi telefon raqam yozadi: `91 690 1966`
2. Bot boshidagi 3 raqamni olib tashlaydi: `6901966`
3. Bazada qidiradi va natijani xabar beradi

## Buyruqlar
- `/start` — Botni boshlash
- `/reload` — Ovozlarni API'dan qayta yuklash
- `/stats` — Bazadagi ovozlar soni

## Koyeb Deploy

### 1. Repo tayyorlash
```
git init
git add .
git commit -m "init"
git remote add origin <your-repo-url>
git push
```

### 2. Koyeb Settings
- **Runtime:** Python
- **Build command:** `pip install -r requirements.txt`
- **Run command:** `python main.py`
- **Service type:** Worker (HTTP port yo'q!)

### 3. Environment Variables (Koyeb dashboard > Environment)
```
BOT_TOKEN=xxxxx
OPENBUDGET_API_URL=https://api.openbudget.uz/votes
API_TOKEN=         # agar kerak bo'lsa
```

### 4. Muhim: Koyeb Worker
Bot polling ishlatadi — HTTP server emas.
Koyeb da **Worker** turi tanlang, **Web Service** emas!

## Local ishga tushirish
```bash
pip install -r requirements.txt
cp .env.example .env
# .env faylni to'ldiring
python main.py
```

## API format moslashtirish
Agar OpenBudget API boshqa maydon nomlari qaytarsa,
`database.py` → `load_votes_from_api()` funksiyasida
`phone_raw = item.get("phone")` qismini o'zgartiring.
