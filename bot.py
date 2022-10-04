import os
import sys
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters
)

async def echo(update, context):
    msg = update.message.text
    chat_id = update.effective_chat.id
    print(f"[{chat_id}]: {msg}")
    await context.bot.send_message(chat_id=chat_id, text=msg)

token = os.getenv("TELEGRAM_BOT_API_TOKEN")
if not token:
    print("please specify env var TELEGRAM_BOT_API_TOKEN", file=sys.stderr)
app = ApplicationBuilder().token(token).build()
echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
app.add_handler(echo_handler)
app.run_polling()

