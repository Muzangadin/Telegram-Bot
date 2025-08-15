from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask, request
import os

TOKEN = "8162201601:AAFOBu_1ddni1jkNeqw1c-cts5EdKA4p1Ls"
app_bot = ApplicationBuilder().token(TOKEN).build()
flask_app = Flask('')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("البوت شغال ✅")

app_bot.add_handler(CommandHandler("start", start))

@flask_app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), app_bot.bot)
    app_bot.update_queue.put(update)
    return "ok"

if __name__ == "__main__":
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    app_bot.bot.set_webhook(url=webhook_url)
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)
