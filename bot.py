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
    keyboard = [[InlineKeyboardButton("🔥 Inizia Creazione HD", callback_data="step_hair")]]
    await update.message.reply_text("Benvenuto nel generatore ultra-realistico avanzato. Scegli le opzioni per iniziare:", reply_markup=InlineKeyboardMarkup(keyboard))

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

    # 4. Densità peli pubici
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
            # Passa alla scelta dell'ambiente
            await mostra_ambienti(query)

    elif data.startswith("density_"):
        context.user_data['density'] = data.split("_")[1]
        await mostra_ambienti(query)

    # 5. Scelta dell'Ambiente / Sfondo
    elif data.startswith("env_"):
        context.user_data['environment'] = data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton("In Piedi / Contro il Muro", callback_data="pos_wall")],
            [InlineKeyboardButton("Sdraiata / Missionaria", callback_data="pos_missionary")],
            [InlineKeyboardButton("A Pecora / In ginocchio", callback_data="pos_doggy")],
            [InlineKeyboardButton("Gambe aperte / Intima", callback_data="pos_spread")]
        ]
        await query.edit_message_text("Seleziona la posizione intima o la postura:", reply_markup=InlineKeyboardMarkup(keyboard))

    # 6. Scelta della Posizione Intima e Generazione Finale
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
    
    # Variabilità dei volti ed etnie per evitare cloni
    faces = [
        "european facial features, soft green eyes, realistic skin",
        "mediterranean facial features, sharp jawline, brown expressive eyes",
        "scandinavian facial features, high cheekbones, striking blue eyes",
        "latina facial features, warm skin tone, deep dark eyes",
        "slavic facial features, delicate nose, piercing gaze"
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

    env_map = {
        'bedroom': 'cozy modern bedroom interior background, warm ambient lighting, bokeh',
        'hotel': 'luxurious high-end hotel room suite, elegant background decor, soft lighting',
        'bathroom': 'modern luxury bathroom, steamy atmosphere, tiled background, soft reflections',
        'balcony': 'private balcony at night, distant city lights bokeh background'
    }
    environment = env_map.get(context.user_data.get('environment'), 'cozy modern bedroom background')

    pos_map = {
        'wall': 'standing against a wall, seductive provocative pose, full body explicit view',
        'missionary': 'lying on back, highly seductive expression, intimate angle, legs open',
        'doggy': 'on hands and knees, arching back, provocative explicit pose',
        'spread': 'lying down, legs spread wide, extremely intimate angle, explicit view'
    }
    position = pos_map.get(context.user_data.get('position'), 'seductive intimate pose')

    # Seed casuale per garantire varietà assoluta a ogni generazione
    random_seed = random.randint(1, 999999)

    # Prompt ottimizzato per il massimo fotorealismo HD e dettagli espliciti
    final_prompt = (
        f"raw explicit unedited candid DSLR photo of a gorgeous unique woman, {position}, "
        f"{hair} hair, {random_face}, {body}, {pubic_desc}, "
        f"{environment}, professional studio lighting, 85mm lens, f/1.4, sharp focus on skin texture, micro-pores, "
        f"natural skin imperfections, subsurface scattering, masterpiece, 4k resolution"
    )

    await query.edit_message_text("⏳ Applicazione ambiente, posizione e rendering HD in corso...")

    encoded_prompt = urllib.parse.quote(final_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=1152&nologo=true&seed={random_seed}"

    await context.bot.send_photo(
        chat_id=query.message.chat_id,
        photo=image_url,
        caption=(
            f"✅ **Immagine HD Personalizzata**\n\n"
            f"👤 **Variante:** {random_seed}\n"
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
    print("Bot avanzato con posizioni e sfondi avviato!")
    app.run_polling()

if __name__ == '__main__':
    main()
