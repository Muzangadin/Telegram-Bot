import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask, request
from keep_alive import keep_alive
import requests

# --- Keep Alive Server ---
keep_alive()

# --- Telegram Bot Token ---
TOKEN = os.environ.get("BOT_TOKEN")  # ضعي توكن البوت في Environment Variables

# --- Google Service Account ---
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_JSON")  # الصقي نص JSON كامل في Environment Variables
info = json.loads(SERVICE_ACCOUNT_JSON)
credentials = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

# --- Subjects and Folders ---
subjects = {
    "radiology": "📸 أشعة",
    "nursing": "🏥 تمريض",
    "geology": "🌍 جولوجيا",
    "pharmacy": "💊 صيدلة",
    "medicine": "طب",
    "dentistry": "🦷 طب أسنان",
    "psychology": "🧠 علم نفس",
    "cs": "📚 علوم حاسوب",
    "law": "⚖️ قانون",
    "labs": "🔬 مختبرات",
    "engineering": "⚙️ هندسة"
}

folders = {
    "radiology": "1qGLVIb71JhHEmTHdBvnThXrlsGhwDdoh",
    "nursing": "1z4Zh1eFeweIi7izDsNUO2nlG_Iei48k4",
    "geology": "11GTK13elJF9cAPQtnaPz4aUN5Oi0PwRm",
    "pharmacy": "1sOojMbVHyLLia4HG6Iz-d92WOA4fGfil",
    "medicine": "rzgrdD1sIP0JPNluUoBDg28paEUhP7-W",
    "dentistry": "1IpK4BnkPWdzARyPiFvVhvcAY_efcBgkc",
    "psychology": "13-Rq9JA1iWnbqsEM2WQ6w5pdBgzCzLHP",
    "cs": "16HgccDzkp4gAkEnDpz1kj3BFsfVxvYeS",
    "law": "1fMzDXxb3Xiz5wB92eE6H7ziiSLjPKgTK",
    "labs": "1jXElSpXAGwNRDLoHB_sz2DbkBShQtsHa",
    "engineering": "17ypQxWyVZ_5PdixUo0Gop4p-0YiP0csx"
}

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(name, callback_data=key)] for key, name in subjects.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر التخصص:", reply_markup=reply_markup)

async def handle_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    subject = query.data
    folder_id = folders.get(subject)
    if not folder_id:
        await query.edit_message_text("لا يوجد مجلد مخصص لهذا التخصص.")
        return

    results = drive_service.files().list(
        q=f"'{folder_id}' in parents and trashed = false",
        fields="files(id, name, webViewLink)"
    ).execute()

    files = results.get('files', [])
    if not files:
        await query.edit_message_text(f"لا توجد محاضرات مرفوعة لتخصص {subjects[subject]}.")
        return

    keyboard = [[InlineKeyboardButton(file['name'], url=file['webViewLink'])] for file in files]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=f"محاضرات تخصص {subjects[subject]}:", reply_markup=reply_markup)

# --- Flask App for Webhook ---
app = Flask(__name__)
bot_app = ApplicationBuilder().token(TOKEN).build()
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(handle_subject, pattern="^(radiology|nursing|geology|pharmacy|medicine|dentistry|psychology|cs|law|labs|engineering)$"))

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    bot_app.dispatcher.process_update(update)
    return "ok"

@app.route('/')
def index():
    return "Bot is alive!"

# --- Set Webhook ---
WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_URL")  # Render يعطي هذا الرابط تلقائي
requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}/{TOKEN}")

# --- Run Flask ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # إذا PORT غير موجود، استخدم 8080 كافتراضي
    app.run(host="0.0.0.0", port=port)
