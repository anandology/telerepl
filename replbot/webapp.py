from flask import Flask, jsonify, request, abort
from .db import Task

app = Flask(__name__)

@app.route("/tasks", methods=["POST"])
def get_task():
    task = Task.get_pending_task()
    if task:
        session = task.get_session()
        d = {
            "id": task.id,
            "code": task.message,
            "state_path": session.state_path,
            "task_url": f"/tasks/{task.id}"
        }
    else:
        d = {}
    return jsonify(dict(d))

@app.route("/tasks/<int:task_id>", methods=["POST"])
def update_task(task_id):
    d = request.get_json()
    task = Task.find(id=task_id)
    if not task:
        return abort(404)

    task.mark_completed(
        exit_status=d['exit_status'],
        stdout=d['stdout'],
        stderr=d['stderr'],
        image_path=d.get('image_path'))

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run()