# 🤖 Kompaniya Mahsulotlari Telegram Bot

Ko'p tilli (O'zbek / Rus / Ingliz) mahsulot katalogi boti.

---

## 📁 Fayllar

| Fayl | Vazifasi |
|------|----------|
| `bot.py` | Botning asosiy kodi |
| `data.py` | Kategoriya va mahsulot ma'lumotlari |
| `requirements.txt` | Kerakli kutubxonalar |

---

## 🚀 Ishga tushirish

### 1. Bot tokeni olish
1. Telegramda [@BotFather](https://t.me/BotFather) ga o'ting
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting
4. Token oling (shunday ko'rinishda: `123456:ABC-DEF...`)

### 2. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 3. Token o'rnatish

**Variant A — muhit o'zgaruvchisi (tavsiya etiladi):**
```bash
export BOT_TOKEN="SIZNING_TOKENINGIZ"
python bot.py
```

**Variant B — `bot.py` ichida to'g'ridan-to'g'ri:**
```python
TOKEN = "SIZNING_TOKENINGIZ"
```

---

## ✏️ Mahsulot qo'shish / tahrirlash (`data.py`)

### Yangi kategoriya qo'shish
```python
CATEGORIES = {
    "yangi_kat": {
        "name": {
            "uz": "🔧 Yangi Kategoriya",
            "ru": "🔧 Новая Категория",
            "en": "🔧 New Category",
        }
    },
}
```

### Yangi mahsulot qo'shish
```python
PRODUCTS = {
    "yangi_kat": {
        "mahsulot_id": {
            "name": {"uz": "Nomi", "ru": "Название", "en": "Name"},
            "price": {"uz": "100,000 so'm", "ru": "9 $", "en": "$9"},
            "usage": {
                "uz": "Mahsulot haqida qisqacha ma'lumot.",
                "ru": "Краткое описание товара.",
                "en": "Brief description of the product.",
            },
            "image": "https://rasm-url.com/rasm.jpg",  # yoki None
        },
    },
}
```

### Rasm qo'shish
- **URL** — to'g'ridan-to'g'ri rasm havolasi
- **Telegram file_id** — avval botga rasm yuboring, file_id oling
- **None** — rasmsiz (faqat matn ko'rsatiladi)

---

## 🌐 Bot imkoniyatlari

- ✅ 3 tilda ishlaydi (O'zbek, Rus, Ingliz)
- ✅ Kategoriyalar bo'yicha mahsulotlar
- ✅ Har bir mahsulotda: rasm, tavsif, narx
- ✅ Orqaga qaytish tugmalari
- ✅ Tilni istalgan vaqt o'zgartirish

---

## 📞 Yordam
Savollar bo'lsa, kodni tahrirlashda Claude bilan ishlashda davom eting!
