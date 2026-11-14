import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Your bot is working.")

def main():
    token = os.getenv("BOT_TOKEN")
    url = os.getenv("RENDER_EXTERNAL_URL")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", "10000")),
        url_path="telegram",
        webhook_url=f"{url}/telegram"
)
if __name__ == "__main__":
    main()
