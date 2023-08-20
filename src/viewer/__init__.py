import math
from typing import Sequence

from junctions.types import Arc, Junction, Lane, Road
from pyglet import app, graphics, shapes, window
from pyglet.math import Mat4, Vec2, Vec3


def node_markers(lane: Lane, batch: shapes.Batch) -> Sequence[shapes.ShapeBase]:
    a = shapes.Circle(
        x=lane.start.x,
        y=lane.start.y,
        radius=1.5,
        color=(240, 200, 10, 255),
        batch=batch,
    )
    b = shapes.Circle(
        x=lane.end.x,
        y=lane.end.y,
        radius=1.5,
        color=(240, 200, 10, 255),
        batch=batch,
    )
    return (a, b)


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

                self.junctions[junction] = (
                    lane_a,
                    lane_b,
                    *node_markers(lanes[0], self.batch),
                    *node_markers(lanes[1], self.batch),
                )

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
                self.junctions[junction] = (
                    *lane_a,
                    *lane_b,
                    *node_markers(lanes[0], self.batch),
                    *node_markers(lanes[1], self.batch),
                )

    def draw(self):
        self.batch.draw()


def run():
    win = window.Window(width=500, height=500)
    scene = Scene()

    @win.event
    def on_draw():
        win.clear()
        scene.draw()

    # Double the scale
    win.view = Mat4.from_scale(Vec3(2, 2, 1))
    road_a = Road((20, 50), bearing=math.pi / 2, road_length=40, lane_separation=8)
    road_b = Road((60, 50), bearing=math.pi / 2, road_length=28, lane_separation=8)
    road_c = Road((88, 50), bearing=math.pi / 2, road_length=40, lane_separation=8)

    curve_a = Arc(
        (70, 68),
        bearing=math.pi,
        arc_radius=10,
        arc_length=math.pi / 2,
        lane_separation=8,
    )
    curve_b = Arc(
        (88, 58),
        bearing=3 * math.pi / 2,
        arc_radius=10,
        arc_length=math.pi / 2,
        lane_separation=8,
    )

    road_d = Road(
        (curve_a.lanes[1].end.x, curve_a.lanes[1].end.y),
        bearing=0,
        road_length=50,
        lane_separation=8,
    )
    scene.add_junction(road_a)
    scene.add_junction(road_b)
    scene.add_junction(road_c)
    scene.add_junction(curve_a)
    scene.add_junction(curve_b)
    scene.add_junction(road_d)
    app.run()
