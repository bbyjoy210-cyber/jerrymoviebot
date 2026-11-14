import os
import uuid
import sqlite3

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
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

CHANNEL_ID = -1004394045407
CHANNEL_LINK = "https://t.me/+7nd_UEdHcj4xMWVl"
DB_NAME = "movies.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            code TEXT PRIMARY KEY,
            file_id TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_video(code, file_id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute(
        "INSERT INTO videos (code, file_id) VALUES (?, ?)",
        (code, file_id)
    )
    conn.commit()
    conn.close()

def get_video(code):
    conn = sqlite3.connect(DB_NAME)
    result = conn.execute(
        "SELECT file_id FROM videos WHERE code = ?",
        (code,)
    ).fetchone()
    conn.close()
    return result[0] if result else None

async def check_join(user_id, context):
    try:
        member = await context.bot.get_chat_member(
            chat_id=CHANNEL_ID,
             user_id=user_id
        )
        return member.status in [
            "member",
            "administrator",
            "creator"
        ]
    except Exception:
        return False

async def send_movie(message, context, code):
    file_id = get_video(code)

    if not file_id:
        await message.reply_text("❌ Video not found.")
        return

    await message.reply_video(file_id)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "🎬 Welcome!\nSend a video to the bot to create a movie link."
        )
        return

    code = context.args[0]

    joined = await check_join(
        update.effective_user.id,
         context
    )

    if joined:
        await send_movie(update.message, context, code)
        return

    keyboard = [
        [
            InlineKeyboardButton(
                "📢 JOIN CHANNEL",
                url=CHANNEL_LINK
            )
          ],
        [
            InlineKeyboardButton(
                "✅ I JOINED",
                callback_data=f"check_{code}"
            )
        ]
    ]

    await update.message.reply_text(
        "🔒 Please join our channel first.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
async def check_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    code = query.data.replace("check_", "", 1)

    joined = await check_join(
        query.from_user.id,
        context
    )

    if joined:
        await query.message.reply_text("✅ Join verified!")
        await send_movie(query.message, context, code)
    else:
        await query.answer(
            "❌ Please join the channel first!",
            show_alert=True
        )
async def upload_video(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if update.effective_user.id != ADMIN_ID:
        return

    video = update.message.video

    code = "v_" + uuid.uuid4().hex[:10]

    save_video(code, video.file_id)

    link = f"https://t.me/{BOT_USERNAME}?start={code}"

    await update.message.reply_text(
         f"🎬 Video saved!\n\n"
        f"🔗 Movie Link:\n{link}"
    )
def main():
    token = os.getenv("BOT_TOKEN")
    url = os.getenv("RENDER_EXTERNAL_URL")

    if not token or not url:
        raise RuntimeError("BOT_TOKEN or RENDER_EXTERNAL_URL is missing")

    init_db()

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
