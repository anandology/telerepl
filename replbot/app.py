"""The bot application.
"""
import asyncio
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    filters
)
from .request import Request
from .db import Session, Task, db

class ReplBot:
    def __init__(self, token):
        self.app = ApplicationBuilder().token(token).build()
        self.add_message_handler()

    def command(self, name):
        """Decorator to register a handler for a command.

            @app.command("/start")
            def start(request):
                return "Welcome!"
        """
        name = name.lstrip("/")
        def decorator(f):
            func = self.make_request_handler(f)
            h = CommandHandler(name, func)
            self.app.add_handler(h)
            return f
        return decorator

    def add_message_handler(self):
        func = self.make_request_handler(self.on_message)
        h = MessageHandler(filters.TEXT & (~filters.COMMAND), func)
        self.app.add_handler(h)

    def run(self):
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.poll_completed())
        self.app.run_polling()

    async def poll_completed(self):
        while True:
            task = Task.find(status="completed", order="id desc")
            if not task:
                # wait for 100 ms before retry
                await asyncio.sleep(1)
                continue

            if task.stdout or task.stderr:
                session = task.get_session()
                msg = f"{task.stdout}{task.stderr}"
                await self.app.bot.send_message(
                        chat_id=session.chat_id,
                        text=msg
                    )
            task.mark_archived()
            await asyncio.sleep(0)

    def make_request_handler(self, func):
        async def handle(update, context):
            print("handler", update, context)
            req = Request(update)
            print('request', req)
            msg = func(req)
            if msg:
                await update.message.reply_text(msg)
        return handle

    def on_message(self, request):
        """Called on every new message.
        """
        with db.transaction():
            session = Session.find(chat_id=request.chat_id)
            if session is None:
                user = request.user
                session = Session.new(
                    chat_id=request.chat_id,
                    user_id=user.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    username=user.username
                )
            msg = session.new_request(request.message_id, request.text)
            task = msg.create_task()
            return f"Created new message: {dict(msg)}\n\nand task: {dict(task)}"
