"""The Request object to capture the message send from telegram.
"""

class Request:
    def __init__(self, update):
        self.update = update

    @property
    def text(self):
        return self.update.message.text

    @property
    def user(self):
        return self.update.effective_user

    @property
    def chat_id(self):
        return self.update.effective_chat.id

    @property
    def message_id(self):
        return self.update.message.id
