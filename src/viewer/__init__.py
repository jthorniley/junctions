from junctions.types import Road
from pyglet import app, graphics, shapes, window


class Scene:
    def __init__(self):
        self.junctions: dict[Road, tuple[shapes.ShapeBase]] = {}
        self.batch: graphics.Batch = graphics.Batch()

    def add_junction(self, junction: Road):
        base = shapes.Rectangle(
            0,
            0,
            junction.road_length,
            junction.lane_separation * 2,
            color=(102, 255, 80, 255),
            batch=self.batch,
        )
        self.junctions[junction] = (base,)

    def draw(self):
        self.batch.draw()


win = window.Window(width=500, height=500)
scene = Scene()


@win.event
def on_draw():
    win.clear()
    scene.draw()


def run():
    scene.add_junction(Road((0, 0), 0, 100, 4))
    app.run()
