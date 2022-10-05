"""The bot application.
"""
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    filters
)
from .request import Request
from .db import Session, Message, db

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
        self.app.run_polling()

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
