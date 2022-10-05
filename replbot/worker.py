from __future__ import annotations
import requests
import time
from urllib.parse import urljoin
from dataclasses import dataclass, asdict
from typing import Any, Optional
from pathlib import Path
from . import config
import cloudpickle

class Worker:
    def __init__(self, tasks_url):
        self.tasks_url = tasks_url

    def get_task(self):
        pass

    def run(self):
        while True:
            task = requests.post(self.tasks_url, json={}).json()
            if not task:
                time.sleep(0.5)
                continue
            self.handle_task(task)

    def handle_task(self, task):
        print("Handling task", task['id'])

        state_path = f"{config.state_dir}/{task['session_id']}/state.pkl"
        Path(state_path).parent.mkdir(exist_ok=True, parents=True)

        response = self.execute(task['code'], state_path)

        task_url = urljoin(self.tasks_url, task['task_url'])
        d = asdict(response)
        requests.post(task_url, json=d)

    def read_state(self, session_id):
        path = Path(config.state_dir) / str(session_id) / "state.pkl"
        if path.exists():
            return cloudpickle.load(path.open("rb"))
        else:
            return {}

    def save_state(self, session_id, state):
        if state is None:
            return

        path = Path(config.state_dir) / str(session_id) / "state.pkl"
        with path.open("wb") as f:
            cloudpickle.dump(state, f)

    def execute(self, code, state) -> TaskResponse:
        raise NotImplementedError()

@dataclass
class TaskResponse:
    exit_status: int
    stdout: str
    stderr: str
    image_path: Optional[str] = None
    state: Any = None
