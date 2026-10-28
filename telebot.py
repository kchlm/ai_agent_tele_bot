import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
import logging

load_dotenv()
TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
USERS = {int(x) for x in os.environ["ALLOWED_USER_IDS"].split(",") if x}
CHATS = {int(x) for x in os.environ["ALLOWED_CHAT_IDS"].split(",") if x}

logging.basicConfig(level=logging.INFO)

async def handle(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    print(
        f"chat={update.effective_chat.id} type={update.effective_chat.type} "
        f"user={update.effective_user.id} thread={msg.message_thread_id}"
    )
    if update.effective_user.id not in USERS:
        return
    if update.effective_chat.type != "private" and update.effective_chat.id not in CHATS:
        return
    await msg.reply_text(f"Echo: {msg.text}")


app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
app.run_polling()