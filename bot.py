import os
import uuid

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

ADMIN_ID = 8055105404
BOT_USERNAME = "J3rryMovie_bot"

CHANNEL_ID = None
CHANNEL_LINK = "https://t.me/+7nd_UEdHcj4xMWVl"

async def check_join(user_id, context):
    try:
        member = await context.bot.get_chat_member(
            chat_id=CHANNEL_ID,
            user_id=user_id
        )
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

async def send_movie(update, context, code):
    videos = context.application.bot_data.setdefault("videos", {})

    if code not in videos:
        await update.effective_message.reply_text("Video not found.")
        return

    await update.effective_message.reply_video(videos[code])
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Welcome! Send a video to the bot.")
        return

    code = context.args[0]
    joined = await check_join(update.effective_user.id, context)

    if joined:
        await send_movie(update, context, code)
        return

    keyboard = [
        [InlineKeyboardButton("📢 JOIN CHANNEL", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ I JOINED", callback_data=f"check_{code}")]
    ]

    await update.message.reply_text(
        "🔒 Please join our channel first to watch this movie.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
async def check_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    code = query.data.replace("check_", "", 1)

    joined = await check_join(query.from_user.id, context)

    if joined:
        await query.message.reply_text("✅ Join verified!")
        await send_movie(query, context, code)
else:
    await query.answer(
        "❌ You haven't joined the channel yet!",
        show_alert=True
    )
    
async def upload_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    video = update.message.video
    code = "v_" + uuid.uuid4().hex[:10]

    videos = context.application.bot_data.setdefault("videos", {})
    videos[code] = video.file_id

    link = f"https://t.me/{BOT_USERNAME}?start={code}"

    await update.message.reply_text(
        f"🎬 Video saved!\n\n🔗 Movie Link:\n{link}"
    )
def main():
    token = os.getenv("BOT_TOKEN")
    url = os.getenv("RENDER_EXTERNAL_URL")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_button))
    app.add_handler(MessageHandler(filters.VIDEO, upload_video))

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", "10000")),
        url_path="telegram",
        webhook_url=f"{url}/telegram"
    )
if __name__ == "__main__":
    main()
