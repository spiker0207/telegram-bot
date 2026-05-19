import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
from data import CATEGORIES, PRODUCTS

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ── Tillar ──────────────────────────────────────────────────────────────────

LANGUAGES = {
    "uz": "🇺🇿 O'zbek",
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
}

TEXTS = {
    "welcome": {
        "uz": "👋 Xush kelibsiz! Iltimos, tilni tanlang:",
        "ru": "👋 Добро пожаловать! Пожалуйста, выберите язык:",
        "en": "👋 Welcome! Please choose your language:",
    },
    "choose_category": {
        "uz": "📦 Kategoriyani tanlang:",
        "ru": "📦 Выберите категорию:",
        "en": "📦 Choose a category:",
    },
    "choose_product": {
        "uz": "🛒 Mahsulotni tanlang:",
        "ru": "🛒 Выберите товар:",
        "en": "🛒 Choose a product:",
    },
    "price": {
        "uz": "💰 Narxi",
        "ru": "💰 Цена",
        "en": "💰 Price",
    },
    "usage": {
        "uz": "📌 Ishlatilishi",
        "ru": "📌 Применение",
        "en": "📌 Usage",
    },
    "back_categories": {
        "uz": "⬅️ Kategoriyalarga qaytish",
        "ru": "⬅️ Назад к категориям",
        "en": "⬅️ Back to categories",
    },
    "back_products": {
        "uz": "⬅️ Mahsulotlarga qaytish",
        "ru": "⬅️ Назад к товарам",
        "en": "⬅️ Back to products",
    },
    "lang_changed": {
        "uz": "✅ Til o'zgartirildi!",
        "ru": "✅ Язык изменён!",
        "en": "✅ Language changed!",
    },
    "change_lang": {
        "uz": "🌐 Tilni o'zgartirish",
        "ru": "🌐 Сменить язык",
        "en": "🌐 Change language",
    },
}

def t(key: str, lang: str) -> str:
    return TEXTS.get(key, {}).get(lang, TEXTS.get(key, {}).get("uz", key))


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("lang", "uz")


# ── Handlers ─────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tilni tanlash."""
    keyboard = [
        [InlineKeyboardButton(label, callback_data=f"lang_{code}")]
        for code, label in LANGUAGES.items()
    ]
    await update.message.reply_text(
        t("welcome", "uz"),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str = None):
    """Kategoriyalar ro'yxati."""
    if lang is None:
        lang = get_lang(context)
    keyboard = []
    for cat_id, cat_data in CATEGORIES.items():
        name = cat_data["name"].get(lang, cat_data["name"]["uz"])
        keyboard.append([InlineKeyboardButton(name, callback_data=f"cat_{cat_id}")])
    keyboard.append([InlineKeyboardButton(t("change_lang", lang), callback_data="change_lang")])
    text = t("choose_category", lang)
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    lang = get_lang(context)

    # ── Til tanlash ──────────────────────────────────────────────────────────
    if data.startswith("lang_"):
        lang = data.split("_", 1)[1]
        context.user_data["lang"] = lang
        await query.edit_message_text(t("lang_changed", lang))
        await show_categories(update, context, lang)
        return

    if data == "change_lang":
        keyboard = [
            [InlineKeyboardButton(label, callback_data=f"lang_{code}")]
            for code, label in LANGUAGES.items()
        ]
        await query.edit_message_text(
            t("welcome", lang),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    # ── Kategoriya tanlash ───────────────────────────────────────────────────
    if data.startswith("cat_"):
        cat_id = data.split("_", 1)[1]
        context.user_data["current_cat"] = cat_id
        products = PRODUCTS.get(cat_id, {})
        keyboard = []
        for prod_id, prod_data in products.items():
            name = prod_data["name"].get(lang, prod_data["name"]["uz"])
            keyboard.append([InlineKeyboardButton(name, callback_data=f"prod_{prod_id}")])
        keyboard.append([InlineKeyboardButton(t("back_categories", lang), callback_data="back_cats")])
        await query.edit_message_text(
            t("choose_product", lang),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    # ── Kategoriyalarga qaytish ──────────────────────────────────────────────
    if data == "back_cats":
        await show_categories(update, context, lang)
        return

    # ── Mahsulotlarga qaytish ────────────────────────────────────────────────
    if data == "back_prods":
        cat_id = context.user_data.get("current_cat")
        if cat_id:
            # Simulate cat_ callback
            query.data = f"cat_{cat_id}"
            await callback_handler(update, context)
        return

    # ── Mahsulot tanlash ─────────────────────────────────────────────────────
    if data.startswith("prod_"):
        prod_id = data.split("_", 1)[1]
        cat_id = context.user_data.get("current_cat")
        prod = PRODUCTS.get(cat_id, {}).get(prod_id)
        if not prod:
            await query.edit_message_text("Mahsulot topilmadi.")
            return

        name    = prod["name"].get(lang, prod["name"]["uz"])
        price   = prod["price"].get(lang, prod["price"]["uz"])
        usage   = prod["usage"].get(lang, prod["usage"]["uz"])
        image   = prod.get("image")  # URL yoki file_id

        caption = (
            f"🏷 <b>{name}</b>\n\n"
            f"{t('usage', lang)}: {usage}\n\n"
            f"{t('price', lang)}: <b>{price}</b>"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t("back_products", lang), callback_data="back_prods")],
            [InlineKeyboardButton(t("back_categories", lang), callback_data="back_cats")],
        ])

        if image:
            await query.message.reply_photo(
                photo=image,
                caption=caption,
                parse_mode="HTML",
                reply_markup=keyboard,
            )
            await query.delete_message()
        else:
            await query.edit_message_text(
                caption,
                parse_mode="HTML",
                reply_markup=keyboard,
            )
        return


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    import os
    TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))
    print("✅ Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
