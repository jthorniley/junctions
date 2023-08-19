import math
from typing import Sequence

from junctions.types import Arc, Junction, Road
from pyglet import app, graphics, shapes, window
from pyglet.math import Mat4, Vec2, Vec3


class Scene:
    def __init__(self):
        self.junctions: dict[Junction, Sequence[shapes.ShapeBase]] = {}
        self.batch: graphics.Batch = graphics.Batch()

    def add_junction(self, junction: Junction):
        match junction:
            case Road():
                lanes = junction.lanes
                lane_a = shapes.Line(
                    lanes[0].start.x,
                    lanes[0].start.y,
                    lanes[0].end.x,
                    lanes[0].end.y,
                    color=(103, 240, 90, 255),
                    batch=self.batch,
                )
                lane_b = shapes.Line(
                    lanes[1].start.x,
                    lanes[1].start.y,
                    lanes[1].end.x,
                    lanes[1].end.y,
                    color=(103, 240, 90, 255),
                    batch=self.batch,
                )

                self.junctions[junction] = (lane_a, lane_b)
            case Arc():
                lanes = junction.lanes
                a0 = lanes[0].start
                b1 = lanes[1].end
                focus = junction.focus

                def make_line(start_point, r):
                    point = start_point
                    lines = []
                    n_points = int(max(10, (r**2) / 10))
                    for i in range(n_points):
                        angle = -junction.bearing - junction.arc_length * (
                            i / (n_points - 1)
                        )
                        next_point = focus + Vec2(-r, 0).rotate(angle)
                        lines.append(
                            shapes.Line(
                                point.x,
                                point.y,
                                next_point.x,
                                next_point.y,
                                color=(103, 240, 90, 255),
                                batch=self.batch,
                            )
                        )
                        point = next_point

                    return lines

                lane_a = make_line(a0, junction.arc_radius)
                b_radius = junction.arc_radius + junction.lane_separation
                lane_b = make_line(b1, b_radius)
                self.junctions[junction] = (*lane_a, *lane_b)

    def draw(self):
        self.batch.draw()


win = window.Window(width=500, height=500)
scene = Scene()


@win.event
def on_draw():
    win.clear()
    scene.draw()


def run():
    # Double the scale
    win.view = Mat4.from_scale(Vec3(2, 2, 1))
    scene.add_junction(Road((20, 10), bearing=0, road_length=100, lane_separation=8))
    scene.add_junction(
        Arc(
            origin=(20, 110),
            bearing=0,
            arc_length=math.pi / 2,
            arc_radius=10,
            lane_separation=8,
        )
    )
    scene.add_junction(
        Arc(
            origin=(30, 120),
            bearing=math.pi / 2,
            arc_length=math.pi / 2,
            arc_radius=10,
            lane_separation=8,
        )
    )
    app.run()
