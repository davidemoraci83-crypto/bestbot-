import logging
import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
from duckduckgo_search import DDGS

# Configurazione dei log
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Server web Flask per mantenere attivo Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is active and running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao! Scrivimi cosa cerchi e ti invierò la foto corrispondente.")

async def search_and_send_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    query = update.message.text.strip()
    await update.message.reply_text(f"⏳ Cerco immagini per: {query}...")

    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(query, max_results=1))
            
        if results:
            image_url = results['image']
            await update.message.reply_photo(photo=image_url)
        else:
            await update.message.reply_text("❌ Nessuna immagine trovata per questa ricerca.")
            
    except Exception as e:
        logger.error(f"Errore durante la ricerca: {e}")
        await update.message.reply_text("⚠️ Si è verificato un errore durante la ricerca. Riprova tra poco.")

def main():
    # Token ufficiale del bot
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8835501004:AAGTVfVe19s1ZbHxzqVyr1jKtFW8rtj2b0")
    
    if not TOKEN:
        logger.error("Errore: Token del bot Telegram non trovato!")
        return

    # Avvia Flask in un thread separato
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()

    # Avvia il bot Telegram
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), search_and_send_image))
    
    logger.info("Bot avviato correttamente e in ascolto...")
    application.run_polling()

if __name__ == '__main__':
    main()
