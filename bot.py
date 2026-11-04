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
    keyboard = [[InlineKeyboardButton("🔥 Scegli la tua Star", callback_data="step_hair")]]
    await update.message.reply_text("Benvenuto nel generatore di star e modelle famose. Seleziona le opzioni:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # 1. Colore Capelli / Categoria Star
    if data == "step_hair":
        keyboard = [
            [InlineKeyboardButton("Bionde Famose (Elsa Jean, Abella Danger, ecc.)", callback_data="hair_blonde")],
            [InlineKeyboardButton("More Famose (Lana Rhoades, Mia Khalifa, ecc.)", callback_data="hair_brunette")],
            [InlineKeyboardButton("Rosse Famose (Asa Akira, ecc.)", callback_data="hair_red")],
            [InlineKeyboardButton("Castane Famose (Adriana Chechik, Kendra Lust, ecc.)", callback_data="hair_brown")]
        ]
        await query.edit_message_text("Seleziona il tipo di star:", reply_markup=InlineKeyboardMarkup(keyboard))

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
        await query.edit_message_text("Vuoi includere dettagli sui peli pubici?", reply_markup=InlineKeyboardMarkup(keyboard))

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
    
    # Database esteso con tantissime celebrità reali del settore adulto (Pornhub, Brazzers, X-Art, ecc.)
    stars_map = {
        'blonde': [
            "Elsa Jean face, iconic blonde hair, cute facial features",
            "Abella Danger face, striking dark blonde hair, intense eyes",
            "Riley Reid face, playful expression, blonde hair",
            "Madison Ivy face, gorgeous blonde features",
            "Brandi Love face, mature blonde adult star features",
            "Lilly Bell face, petite blonde model look"
        ],
        'brunette': [
            "Lana Rhoades face, iconic brunette features, piercing eyes",
            "Mia Khalifa face, dark brunette hair, distinctive Middle Eastern features",
            "Angela White face, stunning brunette, voluptuous face structure",
            "Emily Willis face, gorgeous brunette model",
            "Dani Daniels face, artistic dark hair, expressive eyes",
            "Maitland Ward face, stunning brunette adult actress look"
        ],
        'red': [
            "Asa Akira face, iconic Asian-American adult star features, dark red hair styling",
            "Vixen redhead model face, striking features",
            "High-end redhead adult actress face, pale skin, freckles"
        ],
        'brown': [
            "Adriana Chechik face, light brown hair, energetic expression",
            "Kendra Lust face, mature brown hair, attractive milf features",
            "Gianna Michaels face, classic adult star brown hair",
            "Remy LaCroix face, cute brown hair, unique facial structure"
        ]
    }
    
    selected_star_list = stars_map.get(hair, stars_map['blonde'])
    chosen_star = random.choice(selected_star_list)

    body_map = {
        'natural': 'natural slender body, soft hips, realistic skin',
        'large': 'large natural soft breasts, thick thighs, voluptuous curvy body, soft belly',
        'athletic': 'toned athletic physique, firm defined muscles, fit stomach'
    }
    body = body_map.get(context.user_data.get('body'), 'natural body')

    pubic_choice = context.user_data.get('pubic_choice', 'no')
    if pubic_choice == 'yes':
        density = context.user_data.get('density', 'medium')
        if density == 'light':
            pubic_desc = "visible sparse light pubic hair patch, realistic vulva"
        elif density == 'heavy':
            pubic_desc = "extremely thick, heavy, dense full bush of dark pubic hair covering vulva completely, highly detailed realistic pubic hair"
        else:
            pubic_desc = "clear visible moderate natural pubic hair growth, realistic vulva"
    else:
        pubic_desc = "completely shaved smooth clean hairless pubic area, bare skin"

    env_map = {
        'bedroom': 'luxury bedroom interior, professional studio lighting, 4k',
        'hotel': 'high-end luxury hotel suite, professional lighting, cinematic',
        'bathroom': 'modern luxury bathroom, steamy wet environment, professional lighting',
        'balcony': 'private penthouse balcony at night, city lights bokeh'
    }
    environment = env_map.get(context.user_data.get('environment'), 'luxury bedroom interior')

    pos_map = {
        'wall': 'standing against a wall, seductive provocative pose, full body explicit anatomical view',
        'missionary': 'lying on back, seductive expression, wide open legs, explicit anatomical view',
        'doggy': 'on hands and knees, arching back, provocative explicit rear anatomical view',
        'spread': 'lying down, legs spread wide apart, extremely intimate close-up anatomical view, explicit details'
    }
    position = pos_map.get(context.user_data.get('position'), 'seductive intimate pose')

    random_seed = random.randint(1, 9999999)

    # Prompt strutturato per replicare fedelmente i volti delle star con qualità fotografica professionale
    final_prompt = (
        f"professional adult industry photoshoot, uncensored explicit real photography, looking like {chosen_star}, "
        f"{position}, {body}, {pubic_desc}, {environment}, "
        f"RAW photo, Hasselblad camera, 85mm lens, f/1.4, hyper-detailed skin texture, micro-pores, "
        f"natural skin imperfections, professional studio lighting, 4k resolution, masterpiece"
    )

    await query.edit_message_text("⏳ Generazione della star selezionata in corso...")

    encoded_prompt = urllib.parse.quote(final_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=1152&nologo=true&seed={random_seed}"

    await context.bot.send_photo(
        chat_id=query.message.chat_id,
        photo=image_url,
        caption=(
            f"✅ **Star Generata con Successo**\n\n"
            f"🌟 **Riferimento Star:** {chosen_star.split(' face')[0]}\n"
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
    print("Bot Star VIP avviato!")
    app.run_polling()

if __name__ == '__main__':
    main()
