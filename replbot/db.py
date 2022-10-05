import web
from . import config

db = web.database(config.db_url)

CURRENT_TIMESTAMP = web.db.SQLLiteral("CURRENT_TIMESTAMP at time zone 'utc'")

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

    def get_session(self):
        return Session.find(id=self.session_id)

    def update_status(self, status):
        db.update("task", status="in-progress", where="id=$id", vars={"id": self.id})

    def mark_in_progress(self):
        self.update_status("in-progress")

    def mark_completed(self, exit_status, stdout, stderr, image_path):
        db.update("task",
            status="completed",
            exit_status=exit_status,
            stdout=stdout,
            stderr=stderr,
            image_path=image_path,
            t_completed=CURRENT_TIMESTAMP,
            where="id=$id",
            vars={"id": self.id})

    def mark_archived(self):
        self.update_status("archived")

    @classmethod
    def get_pending_task(cls):
        with db.transaction():
            q = "SELECT * FROM task WHERE status='pending' ORDER BY id desc LIMIT 1 FOR UPDATE"
            result = db.query(q)
            if not result:
                return
            task = Task(result[0])
            task.update_status("in-progress")
            return task

    @classmethod
    def get_completed_tasks(cls, limit=10):
        with db.transaction():
            q = "SELECT * FROM task WHERE status='pending' ORDER BY id desc LIMIT 1 FOR UPDATE"
            result = db.query(q)
            if not result:
                return
            task = Task(result[0])
            task.update_status("in-progress")
            return task
