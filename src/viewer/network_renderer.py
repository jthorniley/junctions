from typing import Sequence

import pyglet
from junctions.network import Network
from junctions.types import Arc, Junction, Lane, Road
from pyglet.math import Vec2


def node_markers(
    lane: Lane, batch: pyglet.shapes.Batch
) -> Sequence[pyglet.shapes.ShapeBase]:
    a = pyglet.shapes.Circle(
        x=lane.start.x,
        y=lane.start.y,
        radius=1.5,
        color=(240, 200, 10, 255),
        batch=batch,
    )
    b = pyglet.shapes.Circle(
        x=lane.end.x,
        y=lane.end.y,
        radius=1.5,
        color=(240, 200, 10, 255),
        batch=batch,
    )
    return (a, b)


class NetworkRenderer:
    def __init__(self, network: Network):
        self._network = network

        self.junctions: dict[Junction, Sequence[pyglet.shapes.ShapeBase]] = {}
        self.batch: pyglet.graphics.Batch = pyglet.graphics.Batch()

        for junction in self._network.all_junctions():
            self._add_junction(junction)

    def _add_junction(self, junction: Junction):
        match junction:
            case Road():
                lanes = junction.lanes
                lane_a = pyglet.shapes.Line(
                    lanes[0].start.x,
                    lanes[0].start.y,
                    lanes[0].end.x,
                    lanes[0].end.y,
                    color=(103, 240, 90, 255),
                    batch=self.batch,
                )
                lane_b = pyglet.shapes.Line(
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
                            pyglet.shapes.Line(
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
