
from replbot.worker import Worker, TaskResponse
from pycle import Pycle


class PythonWorker(Worker):
    def execute(self, code, state_path) -> TaskResponse:
        pycle = Pycle(state_path)
        stdout, stderr = pycle.execute(code)
        return TaskResponse(exit_status=0, stdout=stdout, stderr=stderr)

def main():
    url = "http://localhost:5000/tasks"
    w = PythonWorker(url)
    w.run()

if __name__ == "__main__":
    main()