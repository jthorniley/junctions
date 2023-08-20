from typing import Sequence

import pyglet
from junctions.network import Network
from junctions.types import Arc, Junction, Lane, Road
from pyglet.math import Vec2


def _node_markers(
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


def _road_shapes(
    road: Road, batch: pyglet.graphics.Batch
) -> Sequence[pyglet.shapes.ShapeBase]:
    lanes = road.lanes
    lane_a = pyglet.shapes.Line(
        lanes[0].start.x,
        lanes[0].start.y,
        lanes[0].end.x,
        lanes[0].end.y,
        color=(103, 240, 90, 255),
        batch=batch,
    )
    lane_b = pyglet.shapes.Line(
        lanes[1].start.x,
        lanes[1].start.y,
        lanes[1].end.x,
        lanes[1].end.y,
        color=(103, 240, 90, 255),
        batch=batch,
    )

    return (
        lane_a,
        lane_b,
        *_node_markers(lanes[0], batch),
        *_node_markers(lanes[1], batch),
    )


def _arc_shapes(
    arc: Arc, batch: pyglet.graphics.Batch
) -> Sequence[pyglet.shapes.ShapeBase]:
    lanes = arc.lanes
    a0 = lanes[0].start
    b1 = lanes[1].end
    focus = arc.focus

    def make_line(start_point, r):
        point = start_point
        lines = []
        n_points = int(max(10, (r**2) / 10))
        for i in range(n_points):
            angle = -arc.bearing - arc.arc_length * (i / (n_points - 1))
            next_point = focus + Vec2(-r, 0).rotate(angle)
            lines.append(
                pyglet.shapes.Line(
                    point.x,
                    point.y,
                    next_point.x,
                    next_point.y,
                    color=(103, 240, 90, 255),
                    batch=batch,
                )
            )
            point = next_point

        return lines

    lane_a = make_line(a0, arc.arc_radius)
    b_radius = arc.arc_radius + arc.lane_separation
    lane_b = make_line(b1, b_radius)
    return (
        *lane_a,
        *lane_b,
        *_node_markers(lanes[0], batch),
        *_node_markers(lanes[1], batch),
    )


class NetworkRenderer:
    def __init__(self, network: Network):
        self._network: Network = network

        self._junctions: dict[str, Sequence[pyglet.shapes.ShapeBase]] = {}
        self._batch: pyglet.graphics.Batch = pyglet.graphics.Batch()

    def _refresh_batch(self):
        junction_lookup = self._network.junction_lookup
        if junction_lookup.keys() != self._junctions.keys():
            self._junctions = {}
            self._batch = pyglet.graphics.Batch()
            for label, junction in junction_lookup.items():
                self._add_junction(label, junction)

    def draw(self):
        self._refresh_batch()
        self._batch.draw()

    def _add_junction(self, label: str, junction: Junction):
        match junction:
            case Road():
                self._junctions[label] = _road_shapes(junction, self._batch)

            case Arc():
                self._junctions[label] = _arc_shapes(junction, self._batch)
