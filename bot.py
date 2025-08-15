import os
import json
from io import BytesIO
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from keep_alive import keep_alive

keep_alive()

TOKEN = os.environ.get("BOT_TOKEN")
SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_JSON")

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
info = json.loads(SERVICE_ACCOUNT_JSON)
credentials = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

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
        q=f"'{folder_id}' in parents and trashed=false",
        fields="files(id, name)"
    ).execute()
    files = results.get('files', [])

    if not files:
        await query.edit_message_text(f"لا توجد محاضرات مرفوعة لتخصص {subjects[subject]}.")
        return

    await query.edit_message_text(f"جارٍ إرسال الملفات لتخصص {subjects[subject]}...")

    for file in files:
        request = drive_service.files().get_media(fileId=file['id'])
        fh = BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        fh.seek(0)
        await context.bot.send_document(chat_id=query.message.chat_id, document=fh, filename=file['name'])

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_subject, pattern="^(radiology|nursing|geology|pharmacy|medicine|dentistry|psychology|cs|law|labs|engineering)$"))

if __name__ == "__main__":
    import os
    from flask import Flask
    port = int(os.environ.get("PORT", 8080))
    flask_app = Flask(__name__)

    @flask_app.route("/")
    def home():
        return "Bot is alive!"

    flask_app.run(host="0.0.0.0", port=port)
