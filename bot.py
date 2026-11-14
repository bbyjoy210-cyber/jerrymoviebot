import os
import uuid
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

ADMIN_ID = 8055105404
BOT_USERNAME = "J3rryMovie_bot"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    videos = context.application.bot_data.setdefault("videos", {})

    if context.args:
        code = context.args[0]

        if code in videos:
            await update.message.reply_video(videos[code])
        else:
            await update.message.reply_text("Video not found.")
    else:
        await update.message.reply_text("Welcome! Send a video link to start.")
async def upload_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    video = update.message.video
    code = "v_" + uuid.uuid4().hex[:10]

    videos = context.application.bot_data.setdefault("videos", {})
    videos[code] = video.file_id

    link = f"https://t.me/{BOT_USERNAME}?start={code}"

    await update.message.reply_text(
      f"Video saved!\n\nYour link:\n{link}"
    )
def main():
    token = os.getenv("BOT_TOKEN")
    url = os.getenv("RENDER_EXTERNAL_URL")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, upload_video))

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", "10000")),
        url_path="telegram",
        webhook_url=f"{url}/telegram"
    )
if __name__ == "__main__":
    main()
