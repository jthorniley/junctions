from __future__ import annotations

from typing import Sequence

import pyglet
from junctions.network import Network
from junctions.types import Arc, ArcLane, Junction, Lane, Road, Tee


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
        lanes["a"].start.x,
        lanes["a"].start.y,
        lanes["a"].end.x,
        lanes["a"].end.y,
        color=(103, 240, 90, 255),
        batch=batch,
    )
    lane_b = pyglet.shapes.Line(
        lanes["b"].start.x,
        lanes["b"].start.y,
        lanes["b"].end.x,
        lanes["b"].end.y,
        color=(103, 240, 90, 255),
        batch=batch,
    )

    return (
        lane_a,
        lane_b,
        *_node_markers(lanes["a"], batch),
        *_node_markers(lanes["b"], batch),
    )


def _arc_lane_shapes(lane: ArcLane, batch: pyglet.graphics.Batch):
    point = lane.start
    lines = []
    n_points = int(max(10, (lane.radius**2) / 10))
    for i in range(n_points):
        next_point = lane.interpolate(i / (n_points - 1) * lane.length).point
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


def _arc_shapes(
    arc: Arc, batch: pyglet.graphics.Batch
) -> Sequence[pyglet.shapes.ShapeBase]:
    lane_a = _arc_lane_shapes(arc.lanes["a"], batch)
    lane_b = _arc_lane_shapes(arc.lanes["b"], batch)
    return (
        *lane_a,
        *lane_b,
        *_node_markers(arc.lanes["a"], batch),
        *_node_markers(arc.lanes["b"], batch),
    )


def _tee_shapes(
    tee: Tee, batch: pyglet.graphics.Batch
) -> Sequence[pyglet.shapes.ShapeBase]:
    return (
        *_road_shapes(tee.main_road, batch),
        *_arc_shapes(tee.branch_a, batch),
        *_arc_shapes(tee.branch_b, batch),
    )


class NetworkRenderer:
    def __init__(self, network: Network):
        self._junctions: dict[str, Sequence[pyglet.shapes.ShapeBase]] = {}

        self._batch: pyglet.graphics.Batch = pyglet.graphics.Batch()
        for junction_label in network.junction_labels():
            junction = network.junction(junction_label)
            self._add_junction(junction_label, junction)

    def draw(self):
        self._batch.draw()

    def _add_junction(self, label: str, junction: Junction):
        match junction:
            case Road():
                self._junctions[label] = _road_shapes(junction, self._batch)

            case Arc():
                self._junctions[label] = _arc_shapes(junction, self._batch)

            case Tee():
                self._junctions[label] = _tee_shapes(junction, self._batch)
