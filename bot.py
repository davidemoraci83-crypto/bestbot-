import logging
import urllib.parse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
from flask import Flask
import threading

TOKEN = "8648834944:AAGiLmD4Yz7wysj6IJDLWeZl9185LDNUOSQ"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot Telegram attivo!"

def run_flask():
    web_app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_flask, daemon=True).start()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔥 Crea Persona Realistica", callback_data="step_hair")]]
    await update.message.reply_text("Benvenuto nel generatore avanzato. Premi per iniziare:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "step_hair":
        keyboard = [
            [InlineKeyboardButton("Bionda", callback_data="hair_blonde"), InlineKeyboardButton("Mora", callback_data="hair_brunette")],
            [InlineKeyboardButton("Rossa", callback_data="hair_red")]
        ]
        await query.edit_message_text("Seleziona il colore dei capelli:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("hair_"):
        context.user_data['hair'] = data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton("Seno Naturale", callback_data="body_natural"), InlineKeyboardButton("Seno Grande / Curvy", callback_data="body_large")],
        ]
        await query.edit_message_text("Seleziona la corporatura e il seno:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("body_"):
        context.user_data['body'] = data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton("Con Peli Pubici", callback_data="pubic_yes"), InlineKeyboardButton("Rasi / Smooth", callback_data="pubic_no")]
        ]
        await query.edit_message_text("Vuoi includere dettagli sui peli pubici?", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("pubic_"):
        context.user_data['pubic'] = data.split("_")[1]
        
        hair = context.user_data.get('hair', 'blonde')
        body = "large breasts, curvy body" if context.user_data.get('body') == 'large' else "natural body"
        pubic = "detailed pubic hair" if context.user_data.get('pubic') == 'yes' else "shaved smooth pubic area"
        
        final_prompt = f"photorealistic raw portrait of a nude woman, full body standing, {hair} hair, {body}, {pubic}, highly detailed skin texture, pores, 8k, masterpiece, professional photography"
        
        await query.edit_message_text("⏳ Generazione dell'immagine in corso... Riceverai il risultato tra pochi secondi.")

        encoded_prompt = urllib.parse.quote(final_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=768&nologo=true"

        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=image_url,
            caption=f"✅ Immagine generata con successo!\n\n**Prompt usato:**\n`{final_prompt}`",
            parse_mode="Markdown"
        )

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot avviato correttamente con Flask!")
    app.run_polling()

if __name__ == '__main__':
    main()
