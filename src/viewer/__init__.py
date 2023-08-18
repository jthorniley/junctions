import math
from typing import Sequence

from junctions.types import Road
from pyglet import app, graphics, shapes, window
from pyglet.math import Vec2


class Scene:
    def __init__(self):
        self.junctions: dict[Road, Sequence[shapes.ShapeBase]] = {}
        self.batch: graphics.Batch = graphics.Batch()

    def add_junction(self, junction: Road):
        a0 = Vec2(*junction.origin)
        course = Vec2(0, junction.road_length).rotate(-junction.bearing)
        a1 = a0 + course
        separation = Vec2(-junction.lane_separation, 0).rotate(-junction.bearing)
        b0 = a1 + separation
        b1 = a0 + separation

        lane_a = shapes.Line(
            a0.x, a0.y, a1.x, a1.y, color=(103, 240, 90, 255), batch=self.batch
        )
        lane_b = shapes.Line(
            b0.x, b0.y, b1.x, b1.y, color=(103, 240, 90, 255), batch=self.batch
        )

        self.junctions[junction] = (lane_a, lane_b)

    def draw(self):
        self.batch.draw()


win = window.Window(width=500, height=500)
scene = Scene()


@win.event
def on_draw():
    win.clear()
    scene.draw()


def run():
    scene.add_junction(Road((20, 10), bearing=0, road_length=100, lane_separation=8))
    scene.add_junction(
        Road((50, 10), bearing=math.pi / 2, road_length=100, lane_separation=8)
    )
    scene.add_junction(
        Road((50, 150), bearing=3 * math.pi / 4, road_length=140, lane_separation=8)
    )
    app.run()
