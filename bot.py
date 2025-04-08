import os
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

COUNTRIES = {
    '🇩🇪 Германия': 'German',
    '🇯🇵 Япония': 'Japanese',
    '🇳🇬 Нигерия': 'Nigerian',
    '🇮🇹 Италия': 'Italian',
}

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Это WorldFaceBot 🌍\nОтправь мне своё селфи — и я покажу, как ты выглядишь в разных странах!"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.message.chat_id] = {'photo': update.message.photo[-1].file_id}
    buttons = [[KeyboardButton(c)] for c in COUNTRIES.keys()]
    await update.message.reply_text(
        "Отлично! Теперь выбери 1 страну для начала:",
        reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True)
    )

def generate_image(country):
    prompt = f"Portrait of a {country} person in traditional national clothes, smiling, studio photo"
    url = "https://api.replicate.com/v1/predictions"
    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "version": "db21e45a3f28b463b9a2e2031443c0cf7e9c38ad7592b66c1eb0a1a4df96ecde",
        "input": {"prompt": prompt}
    }
    response = requests.post(url, json=data, headers=headers)
    prediction = response.json()
    return prediction.get("urls", {}).get("get", "https://via.placeholder.com/300.png?text=Image+processing")

async def handle_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    country_emoji = update.message.text
    if country_emoji in COUNTRIES:
        nationality = COUNTRIES[country_emoji]
        await update.message.reply_text(f"Генерирую твой образ как {country_emoji}...⏳")
        image_url = generate_image(nationality)
        await update.message.reply_photo(photo=image_url, caption=f"{country_emoji}: Вот как ты мог бы выглядеть как {nationality} 😊")
    else:
        await update.message.reply_text("Пожалуйста, выбери страну из списка.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_country))
    app.run_polling()

if __name__ == "__main__":
    main()