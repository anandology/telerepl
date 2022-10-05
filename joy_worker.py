
from email.mime import image
from replbot.worker import Worker, TaskResponse
from pycle import Pycle
import joy
import sys
import cairosvg
import uuid
from pathlib import Path

class JoyWorker(Worker):
    def execute(self, code, state_path) -> TaskResponse:
        self.SHAPES = []

        sys.displayhook = self.displayhook
        pycle = Pycle(state_path)
        pycle.env.update(joy.__dict__)
        stdout, stderr = pycle.execute(code)

        if self.SHAPES:
            image_path = self.get_image(self.SHAPES)
        else:
            image_path = None

        print("stdout:", stdout)
        return TaskResponse(exit_status=0, stdout=stdout, stderr=stderr, image_path=image_path)

    def get_image(self, shapes):
        filename = f"{uuid.uuid4().hex}.png"
        path = Path("images") / filename
        path.parent.mkdir(exist_ok=True)

        shape = joy.Group(shapes)  | joy.Scale(sx=1, sy=-1)
        svg = shape.as_svg()
        w, h = 150, 150
        png = cairosvg.svg2png(svg, output_width=w, output_height=h)
        path.write_bytes(png)
        print("created image", path)
        return str(path)

    def displayhook(self, value):
        if value is None:
            return

        if isinstance(value, joy.Shape):
            self.SHAPES.append(value)
        else:
            print(repr(value))

def main():
    url = "http://localhost:5000/tasks"
    w = JoyWorker(url)
    w.run()

if __name__ == "__main__":
    main()