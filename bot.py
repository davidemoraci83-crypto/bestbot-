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
    keyboard = [[InlineKeyboardButton("🔥 Inizia Creazione Reale HD", callback_data="step_hair")]]
    await update.message.reply_text("Benvenuto nel generatore iper-realistico. Scegli le opzioni per iniziare:", reply_markup=InlineKeyboardMarkup(keyboard))

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

    # 3. Presenza peli pubici
    elif data.startswith("body_"):
        context.user_data['body'] = data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton("Con Peli Pubici", callback_data="pubic_yes")],
            [InlineKeyboardButton("Rasi / Lisci (Smooth)", callback_data="pubic_no")]
        ]
        await query.edit_message_text("Vuoi includere dettagli sui peli pubici?", reply_markup=InlineKeyboardMarkup(keyboard))

    # 4. Densità peli pubici potenziata e reale
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
        await query.edit_message_text("Seleziona la posizione intima:", reply_markup=InlineKeyboardMarkup(keyboard))

    # 6. Posizione e Generazione Finale
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
    
    # Tantissime tipologie di persone, volti ed etnie completamente diverse per evitare i cloni
    faces = [
        "authentic european woman, natural freckles on nose, soft green eyes, realistic face",
        "mediterranean woman, sharp jawline, warm olive skin, thick eyebrows, brown eyes",
        "scandinavian woman, high cheekbones, natural pale skin, striking blue eyes",
        "latina woman, warm honey skin tone, expressive dark eyes, natural lips",
        "slavic woman, delicate features, piercing gray eyes, natural facial structure",
        "mixed race woman, glowing warm skin tone, freckles, beautiful unique dark eyes",
        "balkans woman, strong facial features, expressive hazel eyes, natural look",
        "british woman, rosy cheeks, natural thin lips, soft blue eyes"
    ]
    random_face = random.choice(faces)

    body_map = {
        'natural': 'natural slender realistic body, soft hips, realistic skin folds',
        'large': 'large natural soft breasts, thick thighs, voluptuous curvy body, soft belly fat',
        'athletic': 'toned athletic physique, firm muscles, natural definition, fit stomach'
    }
    body = body_map.get(context.user_data.get('body'), 'natural body')

    pubic_choice = context.user_data.get('pubic_choice', 'no')
    if pubic_choice == 'yes':
        density = context.user_data.get('density', 'medium')
        if density == 'light':
            pubic_desc = "visible sparse light pubic hair patch, natural vagina view"
        elif density == 'heavy':
            # Forziamo in modo drastico la presenza di peli folti e abbondanti visibili
            pubic_desc = "extremely thick, heavy, dense full bush of dark pubic hair covering vulva completely, highly detailed realistic pubic hair, fully natural abundant pubic hair"
        else:
            pubic_desc = "clear visible moderate natural pubic hair growth, realistic vulva"
    else:
        pubic_desc = "completely shaved smooth clean hairless pubic area, bare skin"

    env_map = {
        'bedroom': 'cozy modern bedroom interior background, warm ambient lighting, realistic depth of field',
        'hotel': 'luxurious high-end hotel room suite, elegant background decor, soft interior lighting',
        'bathroom': 'modern luxury bathroom, steamy atmosphere, tiled background, realistic wet reflections',
        'balcony': 'private balcony at night, distant city lights bokeh, realistic night atmosphere'
    }
    environment = env_map.get(context.user_data.get('environment'), 'cozy modern bedroom background')

    pos_map = {
        'wall': 'standing against a wall, seductive provocative pose, full body explicit anatomical view',
        'missionary': 'lying on back, seductive expression, intimate wide open legs angle, explicit anatomical view',
        'doggy': 'on hands and knees, arching back, provocative explicit rear anatomical view',
        'spread': 'lying down, legs spread wide apart, extremely intimate close-up anatomical view, explicit details'
    }
    position = pos_map.get(context.user_data.get('position'), 'seductive intimate pose')

    # Seed casuale e unico per ogni richiesta
    random_seed = random.randint(1, 9999999)

    # Prompt strutturato per rimuovere l'effetto "disegno/illustrazione" e forzare il realismo fotografico estremo
    final_prompt = (
        f"raw unedited amateur smartphone photo, real human being, explicit uncensored photography, "
        f"{position}, {hair} hair, {random_face}, {body}, {pubic_desc}, {environment}, "
        f"imperfect skin texture, visible pores, natural skin blemishes, soft lighting, realistic shadows, "
        f"nofilter, 4k realism, realistic human anatomy"
    )

    await query.edit_message_text("⏳ Generazione in corso con parametri fotorealistici avanzati...")

    encoded_prompt = urllib.parse.quote(final_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=1152&nologo=true&seed={random_seed}"

    await context.bot.send_photo(
        chat_id=query.message.chat_id,
        photo=image_url,
        caption=(
            f"✅ **Immagine Reale HD Generata**\n\n"
            f"👤 **ID Modello Unico:** {random_seed}\n"
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
    print("Bot iper-realistico avviato!")
    app.run_polling()

if __name__ == '__main__':
    main()
