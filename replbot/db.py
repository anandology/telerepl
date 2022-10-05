import web
from . import config

db = web.database(config.db_url)

class BaseModel(web.storage):
    @classmethod
    def find(cls, **kwargs):
        result = cls.find_all(**kwargs, limit=1)
        return result[0] if result else None

    @classmethod
    def find_all(cls, **kwargs):
        result = db.where(cls.TABLE, **kwargs)
        return [cls(row) for row in result]

    @classmethod
    def new(cls, **kwargs):
        id = db.insert(cls.TABLE, **kwargs)
        return cls.find(id=id)

class Session(BaseModel):
    TABLE = "session"

    def new_request(self, message_id, message_text):
        """Records a new message request.
        """
        msg = Message.new(
            session_id=self.id,
            message_id=message_id,
            message=message_text,
            message_type="request",
            content_type="text",
        )
        return msg

class Message(BaseModel):
    TABLE = "message"

    def create_task(self):
        return Task.new(
            session_id=self.session_id,
            message_id=self.id,
            message=self.message)

class Task(BaseModel):
    TABLE = "task"


