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
    await update.message.reply_text("Benvenuto nel generatore avanzato ultra-realistico. Premi per iniziare:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # 1. Colore Capelli
    if data == "step_hair":
        keyboard = [
            [InlineKeyboardButton("Bionda", callback_data="hair_blonde"), InlineKeyboardButton("Mora", callback_data="hair_brunette")],
            [InlineKeyboardButton("Rossa", callback_data="hair_red"), InlineKeyboardButton("Castana", callback_data="hair_brown")]
        ]
        await query.edit_message_text("Seleziona il colore dei capelli:", reply_markup=InlineKeyboardMarkup(keyboard))

    # 2. Corporatura e Seno
    elif data.startswith("hair_"):
        context.user_data['hair'] = data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton("Seno Naturale / Slim", callback_data="body_natural")],
            [InlineKeyboardButton("Seno Grande / Curvy", callback_data="body_large")],
            [InlineKeyboardButton("Atletica / Tonica", callback_data="body_athletic")]
        ]
        await query.edit_message_text("Seleziona la corporatura e il seno:", reply_markup=InlineKeyboardMarkup(keyboard))

    # 3. Presenza peli pubici
    elif data.startswith("body_"):
        context.user_data['body'] = data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton("Con Peli Pubici", callback_data="pubic_yes")],
            [InlineKeyboardButton("Rasi / Lisci (Smooth)", callback_data="pubic_no")]
        ]
        await query.edit_message_text("Vuoi includere dettagli sui peli pubici?", reply_markup=InlineKeyboardMarkup(keyboard))

    # 4. Densità peli pubici (se ha scelto di metterli)
    elif data.startswith("pubic_"):
        choice = data.split("_")[1]
        if choice == "yes":
            context.user_data['pubic_choice'] = "yes"
            keyboard = [
                [InlineKeyboardButton("Leggeri / Naturali (pochi)", callback_data="density_light")],
                [InlineKeyboardButton("Innevati / Moderati (medi)", callback_data="density_medium")],
                [InlineKeyboardButton("Folti / Abbondanti (molti)", callback_data="density_heavy")]
            ]
            await query.edit_message_text("Perfetto. Quanti peli pubici vuoi che siano visibili?", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            context.user_data['pubic_choice'] = "no"
            # Salta direttamente allo stile/posa finale se sono rasi
            await procedi_generazione(query, context)

    # 5. Gestione della densità scelta e generazione finale
    elif data.startswith("density_"):
        context.user_data['density'] = data.split("_")[1]
        await procedi_generazione(query, context)

async def procedi_generazione(query, context):
    hair = context.user_data.get('hair', 'blonde')
    
    body_map = {
        'natural': 'natural body, elegant proportions',
        'large': 'large breasts, thick thighs, curvy voluptuous body',
        'athletic': 'toned athletic body, abs, fit physique'
    }
    body = body_map.get(context.user_data.get('body'), 'natural body')

    pubic_choice = context.user_data.get('pubic_choice', 'no')
    if pubic_choice == 'yes':
        density = context.user_data.get('density', 'medium')
        if density == 'light':
            pubic_desc = "sparse light pubic hair, natural look"
        elif density == 'heavy':
            pubic_desc = "thick dense heavy pubic hair, fully natural"
        else:
            pubic_desc = "natural moderate pubic hair"
    else:
        pubic_desc = "shaved smooth clean pubic area"

    # Prompt ultra-realistico ottimizzato per massimizzare il dettaglio e la qualità fotografica
    final_prompt = (
        f"raw explicit unedited candid portrait of a gorgeous nude woman, full body standing, "
        f"{hair} hair, {body}, {pubic_desc}, "
        f"shot on 35mm lens, f/1.8, professional DSLR photography, hyper-detailed skin texture, "
        f"micro-pores, realistic soft skin blemishes, natural lighting, subsurface scattering, 8k resolution, masterpiece"
    )

    await query.edit_message_text("⏳ Composizione del prompt avanzato e generazione fotorealistica in corso... Attendere qualche secondo.")

    encoded_prompt = urllib.parse.quote(final_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=768&nologo=true&seed=42"

    await context.bot.send_photo(
        chat_id=query.message.chat_id,
        photo=image_url,
        caption=f"✅ Immagine fotorealistica generata!\n\n**Dettagli applicati:**\n- Capelli: {hair}\n- Corpo: {context.user_data.get('body')}\n- Peli pubici: {pubic_choice} ({context.user_data.get('density', 'nessuna')})\n\n**Prompt:**\n`{final_prompt}`",
        parse_mode="Markdown"
    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot avanzato avviato con successo!")
    app.run_polling()

if __name__ == '__main__':
    main()
