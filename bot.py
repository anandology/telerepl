import os
import sys
from pycle import Pycle
from pathlib import Path

from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    filters
)
from telegram import ReplyKeyboardMarkup


async def execute(update, context):
    code = update.message.text
    chat_id = update.effective_chat.id

    p = Path(f"sessions/{chat_id}/env.pkl")
    p.parent.mkdir(parents=True, exist_ok=True)

    pycle = Pycle(str(p))
    stdout, stderr = pycle.execute(code)
    if stdout or stderr:
        await update.message.reply_markdown_v2(f"```\n{stdout}{stderr}\n```")

async def start(update, context):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Welcome to Learn Python Bot!"
    )

token = os.getenv("TELEGRAM_BOT_API_TOKEN")
if not token:
    print("please specify env var TELEGRAM_BOT_API_TOKEN", file=sys.stderr)
app = ApplicationBuilder().token(token).build()

start_handler = CommandHandler('start', start)
app.add_handler(start_handler)

execute_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), execute)
app.add_handler(execute_handler)
app.run_polling()

