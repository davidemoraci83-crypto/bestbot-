import logging
import urllib.parse
import random
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
    keyboard = [[InlineKeyboardButton("🔥 Crea Persona Realistica HD", callback_data="step_hair")]]
    await update.message.reply_text("Benvenuto nel generatore ultra-realistico in alta definizione. Scegli le opzioni per iniziare:", reply_markup=InlineKeyboardMarkup(keyboard))

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

    # 2. Corporatura e Stile Fisico
    elif data.startswith("hair_"):
        context.user_data['hair'] = data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton("Seno Naturale / Slim", callback_data="body_natural")],
            [InlineKeyboardButton("Seno Grande / Curvy", callback_data="body_large")],
            [InlineKeyboardButton("Atletica / Tonica", callback_data="body_athletic")]
        ]
        await query.edit_message_text("Seleziona la corporatura:", reply_markup=InlineKeyboardMarkup(keyboard))

    # 3. Presenza peli pubici
    elif data.startswith("body_"):
        context.user_data['body'] = data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton("Con Peli Pubici", callback_data="pubic_yes")],
            [InlineKeyboardButton("Rasi / Lisci (Smooth)", callback_data="pubic_no")]
        ]
        await query.edit_message_text("Vuoi includere dettagli sui peli pubici?", reply_markup=InlineKeyboardMarkup(keyboard))

    # 4. Densità peli pubici reale e marcata
    elif data.startswith("pubic_"):
        choice = data.split("_")[1]
        if choice == "yes":
            context.user_data['pubic_choice'] = "yes"
            keyboard = [
                [InlineKeyboardButton("Pochi (leggeri / accennati)", callback_data="density_light")],
                [InlineKeyboardButton("Medi (naturali regolari)", callback_data="density_medium")],
                [InlineKeyboardButton("Molti (molto folti / abbondanti)", callback_data="density_heavy")]
            ]
            await query.edit_message_text("Seleziona la quantità esatta di peli pubici:", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            context.user_data['pubic_choice'] = "no"
            await procedi_generazione(query, context)

    elif data.startswith("density_"):
        context.user_data['density'] = data.split("_")[1]
        await procedi_generazione(query, context)

async def procedi_generazione(query, context):
    hair = context.user_data.get('hair', 'blonde')
    
    # Variabilità dei volti, etnie e fattezze per evitare che sembri sempre la stessa persona
    faces = [
        "european facial features, soft green eyes, freckles",
        "mediterranean facial features, sharp jawline, brown eyes",
        "scandinavian facial features, high cheekbones, blue eyes",
        "latina facial features, warm skin tone, expressive dark eyes",
        "slavic facial features, delicate nose, piercing eyes"
    ]
    random_face = random.choice(faces)

    body_map = {
        'natural': 'natural slim body, slender waist',
        'large': 'large natural breasts, thick thighs, voluptuous soft curvy body',
        'athletic': 'toned athletic physique, firm defined muscles, flat stomach'
    }
    body = body_map.get(context.user_data.get('body'), 'natural body')

    pubic_choice = context.user_data.get('pubic_choice', 'no')
    if pubic_choice == 'yes':
        density = context.user_data.get('density', 'medium')
        if density == 'light':
            pubic_desc = "sparse minimal light pubic hair patch"
        elif density == 'heavy':
            pubic_desc = "very thick, dense, full heavy bush of dark pubic hair, completely natural and abundant"
        else:
            pubic_desc = "moderate natural pubic hair growth"
    else:
        pubic_desc = "completely shaved smooth clean hairless pubic area"

    # Seed casuale per garantire che ogni generazione crei una persona completamente diversa e unica
    random_seed = random.randint(1, 999999)

    # Prompt avanzatissimo per altissima qualità (HD/4K look) e variabilità totale
    final_prompt = (
        f"raw explicit unedited candid DSLR photo of an unique gorgeous woman, full body standing, "
        f"{hair} hair, {random_face}, {body}, {pubic_desc}, "
        f"professional studio lighting, 85mm lens, f/1.4, sharp focus on skin texture, micro-pores, "
        f"hyper-realistic details, masterpiece, 4k resolution, award-winning photography"
    )

    await query.edit_message_text("⏳ Generazione in corso con motore ad alta definizione e variabilità casuale...")

    encoded_prompt = urllib.parse.quote(final_prompt)
    # Risoluzione raddoppiata (768x1152) per immagini molto più nitide e dettagliate
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=1152&nologo=true&seed={random_seed}"

    await context.bot.send_photo(
        chat_id=query.message.chat_id,
        photo=image_url,
        caption=(
            f"✅ **Immagine HD Generata con Successo!**\n\n"
            f"👤 **Variante unica** (Seed: {random_seed})\n"
            f"💇‍♀️ **Capelli:** {hair}\n"
            f"📐 **Corpo:** {context.user_data.get('body')}\n"
            f"🌿 **Peli pubici:** {pubic_choice} ({context.user_data.get('density', 'nessuno')})"
        ),
        parse_mode="Markdown"
    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot HD avanzato avviato!")
    app.run_polling()

if __name__ == '__main__':
    main()
