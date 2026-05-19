import logging
import json
import os
import re
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters, ConversationHandler
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

ADMIN_ID = 5988569293

(ADD_CAT_NAME_UZ, ADD_CAT_NAME_RU, ADD_CAT_NAME_EN,
 ADD_ITEM_NAME_UZ, ADD_ITEM_NAME_RU, ADD_ITEM_NAME_EN,
 ADD_ITEM_PRICE_UZ, ADD_ITEM_PRICE_RU, ADD_ITEM_PRICE_EN,
 ADD_ITEM_USAGE_UZ, ADD_ITEM_USAGE_RU, ADD_ITEM_USAGE_EN,
 ADD_ITEM_IMAGE) = range(13)

DATA_FILE = "db.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"categories": {}, "products": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

LANGUAGES = {"uz": "🇺🇿 O'zbek", "ru": "🇷🇺 Русский", "en": "🇬🇧 English"}

TEXTS = {
    "welcome":         {"uz": "👋 Xush kelibsiz! Tilni tanlang:", "ru": "👋 Добро пожаловать! Выберите язык:", "en": "👋 Welcome! Choose language:"},
    "choose_category": {"uz": "📦 Kategoriyani tanlang:", "ru": "📦 Выберите категорию:", "en": "📦 Choose a category:"},
    "choose_product":  {"uz": "🛒 Mahsulotni tanlang:", "ru": "🛒 Выберите товар:", "en": "🛒 Choose a product:"},
    "price":           {"uz": "💰 Narxi", "ru": "💰 Цена", "en": "💰 Price"},
    "usage":           {"uz": "📌 Ishlatilishi", "ru": "📌 Применение", "en": "📌 Usage"},
    "back_categories": {"uz": "⬅️ Kategoriyalarga", "ru": "⬅️ К категориям", "en": "⬅️ Categories"},
    "back_products":   {"uz": "⬅️ Mahsulotlarga", "ru": "⬅️ К товарам", "en": "⬅️ Products"},
    "change_lang":     {"uz": "🌐 Tilni o'zgartirish", "ru": "🌐 Сменить язык", "en": "🌐 Change language"},
    "no_products":     {"uz": "😔 Bu kategoriyada mahsulot yo'q.", "ru": "😔 В этой категории нет товаров.", "en": "😔 No products in this category."},
    "no_categories":   {"uz": "😔 Hali kategoriya yo'q.", "ru": "😔 Категорий пока нет.", "en": "😔 No categories yet."},
}

def t(key, lang):
    return TEXTS.get(key, {}).get(lang, TEXTS.get(key, {}).get("uz", key))

def get_lang(context):
    return context.user_data.get("lang", "uz")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(label, callback_data=f"lang_{code}")] for code, label in LANGUAGES.items()]
    await update.message.reply_text(t("welcome", "uz"), reply_markup=InlineKeyboardMarkup(keyboard))

async def show_categories(update, context, lang=None):
    if lang is None:
        lang = get_lang(context)
    db = load_data()
    cats = db["categories"]
    keyboard = []
    for cat_id, cat in cats.items():
        name = cat["name"].get(lang, cat["name"].get("uz", cat_id))
        keyboard.append([InlineKeyboardButton(name, callback_data=f"cat_{cat_id}")])
    keyboard.append([InlineKeyboardButton(t("change_lang", lang), callback_data="change_lang")])
    text = t("choose_category", lang) if cats else t("no_categories", lang)
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data_str = query.data
    lang = get_lang(context)
    db = load_data()

    if data_str.startswith("lang_"):
        lang = data_str.split("_", 1)[1]
        context.user_data["lang"] = lang
        await show_categories(update, context, lang)
        return

    if data_str == "change_lang":
        keyboard = [[InlineKeyboardButton(label, callback_data=f"lang_{code}")] for code, label in LANGUAGES.items()]
        await query.edit_message_text(t("welcome", lang), reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data_str.startswith("cat_"):
        cat_id = data_str.split("_", 1)[1]
        context.user_data["current_cat"] = cat_id
        products = db["products"].get(cat_id, {})
        keyboard = []
        for prod_id, prod in products.items():
            name = prod["name"].get(lang, prod["name"].get("uz", prod_id))
            keyboard.append([InlineKeyboardButton(name, callback_data=f"prod_{prod_id}")])
        keyboard.append([InlineKeyboardButton(t("back_categories", lang), callback_data="back_cats")])
        text = t("choose_product", lang) if products else t("no_products", lang)
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data_str == "back_cats":
        await show_categories(update, context, lang)
        return

    if data_str == "back_prods":
        cat_id = context.user_data.get("current_cat")
        if cat_id:
            query.data = f"cat_{cat_id}"
            await callback_handler(update, context)
        return

    if data_str.startswith("prod_"):
        prod_id = data_str.split("_", 1)[1]
        cat_id = context.user_data.get("current_cat")
        prod = db["products"].get(cat_id, {}).get(prod_id)
        if not prod:
            await query.edit_message_text("Mahsulot topilmadi.")
            return
        name  = prod["name"].get(lang, prod["name"].get("uz", ""))
        price = prod["price"].get(lang, prod["price"].get("uz", ""))
        usage = prod["usage"].get(lang, prod["usage"].get("uz", ""))
        image = prod.get("image")
        caption = f"🏷 <b>{name}</b>\n\n{t('usage', lang)}: {usage}\n\n{t('price', lang)}: <b>{price}</b>"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t("back_products", lang), callback_data="back_prods")],
            [InlineKeyboardButton(t("back_categories", lang), callback_data="back_cats")],
        ])
        if image:
            await query.message.reply_photo(photo=image, caption=caption, parse_mode="HTML", reply_markup=keyboard)
            await query.delete_message()
        else:
            await query.edit_message_text(caption, parse_mode="HTML", reply_markup=keyboard)
        return

# ── Admin ─────────────────────────────────────────────────────────────────────

def is_admin(update):
    return update.effective_user.id == ADMIN_ID

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return
    await show_admin_panel(update, context)

async def show_admin_panel(update, context, edit=False):
    db = load_data()
    cat_count = len(db["categories"])
    prod_count = sum(len(v) for v in db["products"].values())
    text = f"🛠 <b>Admin Panel</b>\n\n📦 Kategoriyalar: <b>{cat_count}</b>\n🛒 Mahsulotlar: <b>{prod_count}</b>"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Kategoriya qo'shish", callback_data="admin_add_cat")],
        [InlineKeyboardButton("➕ Mahsulot qo'shish", callback_data="admin_add_item")],
        [InlineKeyboardButton("🗑 Kategoriya o'chirish", callback_data="admin_del_cat")],
        [InlineKeyboardButton("🗑 Mahsulot o'chirish", callback_data="admin_del_item")],
        [InlineKeyboardButton("📋 Barchasini ko'rish", callback_data="admin_view_all")],
    ])
    if edit and update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    query = update.callback_query
    await query.answer()
    data_str = query.data
    db = load_data()

    if data_str == "admin_add_cat":
        await query.edit_message_text("📝 Kategoriya nomini <b>O'zbekcha</b> yozing:", parse_mode="HTML")
        return ADD_CAT_NAME_UZ

    if data_str == "admin_add_item":
        cats = db["categories"]
        if not cats:
            await query.edit_message_text("❌ Avval kategoriya qo'shing!\n\n/admin")
            return ConversationHandler.END
        keyboard = [[InlineKeyboardButton(cat["name"].get("uz", cid), callback_data=f"acat_{cid}")] for cid, cat in cats.items()]
        keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_back")])
        await query.edit_message_text("📦 Mahsulot qo'shish uchun kategoriya tanlang:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data_str.startswith("acat_"):
        cat_id = data_str.split("_", 1)[1]
        context.user_data["admin_cat"] = cat_id
        await query.edit_message_text("📝 Mahsulot nomini <b>O'zbekcha</b> yozing:", parse_mode="HTML")
        return ADD_ITEM_NAME_UZ

    if data_str == "admin_del_cat":
        cats = db["categories"]
        if not cats:
            await query.edit_message_text("❌ Kategoriya yo'q!\n\n/admin")
            return
        keyboard = [[InlineKeyboardButton(f"🗑 {cat['name'].get('uz', cid)}", callback_data=f"delcat_{cid}")] for cid, cat in cats.items()]
        keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_back")])
        await query.edit_message_text("🗑 Qaysi kategoriyani o'chirish?", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data_str.startswith("delcat_"):
        cat_id = data_str.split("_", 1)[1]
        cat_name = db["categories"].get(cat_id, {}).get("name", {}).get("uz", cat_id)
        del db["categories"][cat_id]
        if cat_id in db["products"]:
            del db["products"][cat_id]
        save_data(db)
        await query.edit_message_text(f"✅ <b>{cat_name}</b> kategoriyasi o'chirildi!\n\n/admin", parse_mode="HTML")
        return

    if data_str == "admin_del_item":
        cats = db["categories"]
        if not cats:
            await query.edit_message_text("❌ Kategoriya yo'q!\n\n/admin")
            return
        keyboard = [[InlineKeyboardButton(cat["name"].get("uz", cid), callback_data=f"delitemcat_{cid}")] for cid, cat in cats.items()]
        keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_back")])
        await query.edit_message_text("📦 Kategoriyani tanlang:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data_str.startswith("delitemcat_"):
        cat_id = data_str.split("_", 1)[1]
        prods = db["products"].get(cat_id, {})
        if not prods:
            await query.edit_message_text("❌ Bu kategoriyada mahsulot yo'q!\n\n/admin")
            return
        keyboard = [[InlineKeyboardButton(f"🗑 {p['name'].get('uz', pid)}", callback_data=f"delitem_{cat_id}|{pid}")] for pid, p in prods.items()]
        keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_back")])
        await query.edit_message_text("🗑 Qaysi mahsulotni o'chirish?", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data_str.startswith("delitem_"):
        _, rest = data_str.split("_", 1)
        cat_id, prod_id = rest.split("|", 1)
        prod_name = db["products"].get(cat_id, {}).get(prod_id, {}).get("name", {}).get("uz", prod_id)
        if cat_id in db["products"] and prod_id in db["products"][cat_id]:
            del db["products"][cat_id][prod_id]
            save_data(db)
        await query.edit_message_text(f"✅ <b>{prod_name}</b> o'chirildi!\n\n/admin", parse_mode="HTML")
        return

    if data_str == "admin_view_all":
        cats = db["categories"]
        if not cats:
            await query.edit_message_text("❌ Hali hech narsa yo'q!\n\n/admin")
            return
        text = "📋 <b>Barcha ma'lumotlar:</b>\n\n"
        for cid, cat in cats.items():
            text += f"📦 <b>{cat['name'].get('uz', cid)}</b>\n"
            prods = db["products"].get(cid, {})
            for pid, p in prods.items():
                text += f"  └ 🛒 {p['name'].get('uz', pid)} — {p['price'].get('uz', '')}\n"
            if not prods:
                text += "  └ (mahsulot yo'q)\n"
            text += "\n"
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_back")]])
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=keyboard)
        return

    if data_str == "admin_back":
        await show_admin_panel(update, context, edit=True)
        return

# ── Kategoriya conversation ───────────────────────────────────────────────────

async def cat_name_uz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_cat"] = {"uz": update.message.text}
    await update.message.reply_text("📝 Kategoriya nomini <b>Ruscha</b> yozing:", parse_mode="HTML")
    return ADD_CAT_NAME_RU

async def cat_name_ru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_cat"]["ru"] = update.message.text
    await update.message.reply_text("📝 Kategoriya nomini <b>Inglizcha</b> yozing:", parse_mode="HTML")
    return ADD_CAT_NAME_EN

async def cat_name_en(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_cat"]["en"] = update.message.text
    names = context.user_data["new_cat"]
    db = load_data()
    cat_id = re.sub(r'\W+', '_', names["uz"].lower()) + "_" + str(int(time.time()))[-4:]
    db["categories"][cat_id] = {"name": names}
    db["products"][cat_id] = {}
    save_data(db)
    await update.message.reply_text(
        f"✅ Kategoriya qo'shildi!\n\n🇺🇿 {names['uz']}\n🇷🇺 {names['ru']}\n🇬🇧 {names['en']}\n\n/admin",
        parse_mode="HTML"
    )
    return ConversationHandler.END

# ── Mahsulot conversation ─────────────────────────────────────────────────────

async def item_name_uz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_item"] = {"name": {"uz": update.message.text}}
    await update.message.reply_text("📝 Mahsulot nomini <b>Ruscha</b> yozing:", parse_mode="HTML")
    return ADD_ITEM_NAME_RU

async def item_name_ru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_item"]["name"]["ru"] = update.message.text
    await update.message.reply_text("📝 Mahsulot nomini <b>Inglizcha</b> yozing:", parse_mode="HTML")
    return ADD_ITEM_NAME_EN

async def item_name_en(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_item"]["name"]["en"] = update.message.text
    await update.message.reply_text("💰 Narxini <b>O'zbekcha</b> yozing:\n(masalan: 150,000 so'm)", parse_mode="HTML")
    return ADD_ITEM_PRICE_UZ

async def item_price_uz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_item"]["price"] = {"uz": update.message.text}
    await update.message.reply_text("💰 Narxini <b>Ruscha</b> yozing:", parse_mode="HTML")
    return ADD_ITEM_PRICE_RU

async def item_price_ru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_item"]["price"]["ru"] = update.message.text
    await update.message.reply_text("💰 Narxini <b>Inglizcha</b> yozing:", parse_mode="HTML")
    return ADD_ITEM_PRICE_EN

async def item_price_en(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_item"]["price"]["en"] = update.message.text
    await update.message.reply_text("📌 Tavsifini <b>O'zbekcha</b> yozing:", parse_mode="HTML")
    return ADD_ITEM_USAGE_UZ

async def item_usage_uz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_item"]["usage"] = {"uz": update.message.text}
    await update.message.reply_text("📌 Tavsifini <b>Ruscha</b> yozing:", parse_mode="HTML")
    return ADD_ITEM_USAGE_RU

async def item_usage_ru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_item"]["usage"]["ru"] = update.message.text
    await update.message.reply_text("📌 Tavsifini <b>Inglizcha</b> yozing:", parse_mode="HTML")
    return ADD_ITEM_USAGE_EN

async def item_usage_en(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_item"]["usage"]["en"] = update.message.text
    await update.message.reply_text(
        "🖼 Mahsulot rasmini yuboring:\n(rasm bo'lmasa <b>/skip</b> yozing)",
        parse_mode="HTML"
    )
    return ADD_ITEM_IMAGE

async def item_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data["new_item"]["image"] = update.message.photo[-1].file_id
    else:
        context.user_data["new_item"]["image"] = None
    await save_new_item(update, context)
    return ConversationHandler.END

async def item_skip_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_item"]["image"] = None
    await save_new_item(update, context)
    return ConversationHandler.END

async def save_new_item(update, context):
    item = context.user_data["new_item"]
    cat_id = context.user_data["admin_cat"]
    db = load_data()
    prod_id = re.sub(r'\W+', '_', item["name"]["uz"].lower()) + "_" + str(int(time.time()))[-4:]
    if cat_id not in db["products"]:
        db["products"][cat_id] = {}
    db["products"][cat_id][prod_id] = item
    save_data(db)
    await update.message.reply_text(
        f"✅ Mahsulot qo'shildi!\n\n🏷 <b>{item['name']['uz']}</b>\n💰 {item['price']['uz']}\n\n/admin",
        parse_mode="HTML"
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Bekor qilindi.\n\n/admin")
    return ConversationHandler.END

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    app = Application.builder().token(TOKEN).build()

    cat_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_callback, pattern="^admin_add_cat$")],
        states={
            ADD_CAT_NAME_UZ: [MessageHandler(filters.TEXT & ~filters.COMMAND, cat_name_uz)],
            ADD_CAT_NAME_RU: [MessageHandler(filters.TEXT & ~filters.COMMAND, cat_name_ru)],
            ADD_CAT_NAME_EN: [MessageHandler(filters.TEXT & ~filters.COMMAND, cat_name_en)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    item_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_callback, pattern="^acat_")],
        states={
            ADD_ITEM_NAME_UZ:  [MessageHandler(filters.TEXT & ~filters.COMMAND, item_name_uz)],
            ADD_ITEM_NAME_RU:  [MessageHandler(filters.TEXT & ~filters.COMMAND, item_name_ru)],
            ADD_ITEM_NAME_EN:  [MessageHandler(filters.TEXT & ~filters.COMMAND, item_name_en)],
            ADD_ITEM_PRICE_UZ: [MessageHandler(filters.TEXT & ~filters.COMMAND, item_price_uz)],
            ADD_ITEM_PRICE_RU: [MessageHandler(filters.TEXT & ~filters.COMMAND, item_price_ru)],
            ADD_ITEM_PRICE_EN: [MessageHandler(filters.TEXT & ~filters.COMMAND, item_price_en)],
            ADD_ITEM_USAGE_UZ: [MessageHandler(filters.TEXT & ~filters.COMMAND, item_usage_uz)],
            ADD_ITEM_USAGE_RU: [MessageHandler(filters.TEXT & ~filters.COMMAND, item_usage_ru)],
            ADD_ITEM_USAGE_EN: [MessageHandler(filters.TEXT & ~filters.COMMAND, item_usage_en)],
            ADD_ITEM_IMAGE:    [
                MessageHandler(filters.PHOTO, item_image),
                CommandHandler("skip", item_skip_image),
                MessageHandler(filters.TEXT & ~filters.COMMAND, item_skip_image),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(cat_conv)
    app.add_handler(item_conv)
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^admin_"))
    app.add_handler(CallbackQueryHandler(callback_handler))

    print("✅ Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
