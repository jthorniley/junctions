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
            case Road(origin, bearing, road_length, lane_separation):
                a0 = Vec2(*origin)
                course = Vec2(0, road_length).rotate(-bearing)
                a1 = a0 + course
                separation = Vec2(-lane_separation, 0).rotate(-bearing)
                b0 = a1 + separation
                b1 = a0 + separation

                lane_a = shapes.Line(
                    a0.x, a0.y, a1.x, a1.y, color=(103, 240, 90, 255), batch=self.batch
                )
                lane_b = shapes.Line(
                    b0.x, b0.y, b1.x, b1.y, color=(103, 240, 90, 255), batch=self.batch
                )

                self.junctions[junction] = (lane_a, lane_b)
            case Arc(origin, bearing, arc_length, arc_radius, lane_separation):
                # The origin is the a_0 point, we need to work out
                # the focal point of the arc
                a0 = Vec2(*origin)
                origin_tangent = Vec2(0, 1).rotate(-bearing)
                origin_normal = origin_tangent.rotate(math.pi / 2)
                focus = a0 - origin_normal * arc_radius

                def make_line(start_point, r):
                    point = start_point
                    lines = []
                    n_points = int(max(10, (r**2) / 10))
                    for i in range(n_points):
                        angle = -bearing - arc_length * (i / (n_points - 1))
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

                lane_a = make_line(a0, arc_radius)
                b_radius = arc_radius + lane_separation
                lane_b = make_line(focus + origin_normal * b_radius, b_radius)
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
