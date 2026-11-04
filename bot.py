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
    keyboard = [[InlineKeyboardButton("🔥 Inizia Generazione Uncensored", callback_data="step_hair")]]
    await update.message.reply_text("Benvenuto nel generatore avanzato senza censura. Seleziona le opzioni:", reply_markup=InlineKeyboardMarkup(keyboard))

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

    # 2. Corporatura
    elif data.startswith("hair_"):
        context.user_data['hair'] = data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton("Seno Naturale / Slim", callback_data="body_natural")],
            [InlineKeyboardButton("Seno Grande / Curvy", callback_data="body_large")],
            [InlineKeyboardButton("Atletica / Tonica", callback_data="body_athletic")]
        ]
        await query.edit_message_text("Seleziona la corporatura:", reply_markup=InlineKeyboardMarkup(keyboard))

    # 3. Peli pubici
    elif data.startswith("body_"):
        context.user_data['body'] = data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton("Con Peli Pubici", callback_data="pubic_yes")],
            [InlineKeyboardButton("Rasi / Lisci (Smooth)", callback_data="pubic_no")]
        ]
        await query.edit_message_text("Vuoi includere i peli pubici?", reply_markup=InlineKeyboardMarkup(keyboard))

    # 4. Densità
    elif data.startswith("pubic_"):
        choice = data.split("_")[1]
        if choice == "yes":
            context.user_data['pubic_choice'] = "yes"
            keyboard = [
                [InlineKeyboardButton("Pochi (leggeri)", callback_data="density_light")],
                [InlineKeyboardButton("Medi (naturali)", callback_data="density_medium")],
                [InlineKeyboardButton("Molti (folti / abbondanti)", callback_data="density_heavy")]
            ]
            await query.edit_message_text("Seleziona la quantità di peli pubici:", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            context.user_data['pubic_choice'] = "no"
            await mostra_ambienti(query)

    elif data.startswith("density_"):
        context.user_data['density'] = data.split("_")[1]
        await mostra_ambienti(query)

    # 5. Ambiente
    elif data.startswith("env_"):
        context.user_data['environment'] = data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton("In Piedi / Contro il Muro", callback_data="pos_wall")],
            [InlineKeyboardButton("Sdraiata / Missionaria", callback_data="pos_missionary")],
            [InlineKeyboardButton("A Pecora / In ginocchio", callback_data="pos_doggy")],
            [InlineKeyboardButton("Gambe aperte / Intima", callback_data="pos_spread")]
        ]
        await query.edit_message_text("Seleziona la posizione:", reply_markup=InlineKeyboardMarkup(keyboard))

    # 6. Posizione e Generazione
    elif data.startswith("pos_"):
        context.user_data['position'] = data.split("_")[1]
        await procedi_generazione(query, context)

async def mostra_ambienti(query):
    keyboard = [
        [InlineKeyboardButton("Camera da letto moderna", callback_data="env_bedroom")],
        [InlineKeyboardButton("Hotel di lusso", callback_data="env_hotel")],
        [InlineKeyboardButton("Bagno con vapore / Doccia", callback_data="env_bathroom")],
        [InlineKeyboardButton("Balcone privato di notte", callback_data="env_balcony")]
    ]
    await query.edit_message_text("Seleziona l'ambiente dello sfondo:", reply_markup=InlineKeyboardMarkup(keyboard))

async def procedi_generazione(query, context):
    hair = context.user_data.get('hair', 'blonde')
    
    body_map = {
        'natural': 'slim slender body, natural breasts, soft hips',
        'large': 'large natural breasts, thick thighs, voluptuous curvy body, soft belly',
        'athletic': 'toned athletic physique, firm muscles, fit stomach'
    }
    body = body_map.get(context.user_data.get('body'), 'natural body')

    pubic_choice = context.user_data.get('pubic_choice', 'no')
    if pubic_choice == 'yes':
        density = context.user_data.get('density', 'medium')
        if density == 'light':
            pubic_desc = "sparse light pubic hair patch, visible vulva"
        elif density == 'heavy':
            pubic_desc = "extremely thick, heavy, dense full bush of dark pubic hair completely covering vulva, highly detailed realistic pubic hair"
        else:
            pubic_desc = "clear visible moderate natural pubic hair growth, realistic vulva"
    else:
        pubic_desc = "completely shaved smooth clean hairless pubic area"

    env_map = {
        'bedroom': 'modern luxury bedroom interior background, professional cinematic lighting',
        'hotel': 'high-end luxury hotel suite, elegant decor, soft lighting',
        'bathroom': 'modern luxury bathroom, steamy wet environment, mirror reflections',
        'balcony': 'private penthouse balcony at night, distant city lights bokeh'
    }
    environment = env_map.get(context.user_data.get('environment'), 'modern luxury bedroom background')

    pos_map = {
        'wall': 'standing against a wall, full body explicit anatomical view, seductive pose',
        'missionary': 'lying on back, wide open legs, full body explicit anatomical view, intimate angle',
        'doggy': 'on hands and knees, arching back, full body explicit rear anatomical view',
        'spread': 'lying down, legs spread wide apart, full body explicit close-up anatomical view'
    }
    position = pos_map.get(context.user_data.get('position'), 'full body explicit view')

    random_seed = random.randint(1, 99999999)

    # Prompt ottimizzato per il nuovo motore senza censura
    final_prompt = (
        f"masterpiece, raw unedited explicit uncensored photography of a gorgeous woman, "
        f"full body view, {position}, {hair} hair, {body}, {pubic_desc}, {environment}, "
        f"detailed skin texture, pores, professional lighting, 8k resolution, photorealistic"
    )

    await query.edit_message_text("⏳ Generazione con motore Uncensored avanzato in corso...")

    encoded_prompt = urllib.parse.quote(final_prompt)
    # Utilizziamo un endpoint Stable Diffusion alternativo (Pollinations con parametri raw potenziati e seed variabile)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=1024&nologo=true&private=true&model=flux&seed={random_seed}"

    await context.bot.send_photo(
        chat_id=query.message.chat_id,
        photo=image_url,
        caption=(
            f"✅ **Immagine Uncensored Generata**\n\n"
            f"💇‍♀️ **Capelli:** {hair} | **Corpo:** {context.user_data.get('body')}\n"
            f"🌿 **Peli pubici:** {pubic_choice} ({context.user_data.get('density', 'nessuno')})\n"
            f"🏡 **Ambiente:** {context.user_data.get('environment')}\n"
            f"🔥 **Posizione:** {context.user_data.get('position')}"
        ),
        parse_mode="Markdown"
    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot Uncensored avviato con successo!")
    app.run_polling()

if __name__ == '__main__':
    main()
