from __future__ import annotations

from typing import Final, Sequence

import pyglet
from junctions.network import LaneRef, Network
from junctions.state.wait_flags import WaitFlags
from junctions.types import Arc, ArcLane, Junction, Lane, Road, Tee

DEFAULT_LANE_COLOR: Final = (150, 150, 150, 255)
WAIT_LANE_COLOR: Final = (243, 150, 150, 255)


def _node_markers(
    lane: Lane, batch: pyglet.shapes.Batch
) -> Sequence[pyglet.shapes.ShapeBase]:
    a = pyglet.shapes.Circle(
        x=lane.start.x,
        y=lane.start.y,
        radius=1.2,
        color=(240, 200, 200, 255),
        batch=batch,
    )
    b = pyglet.shapes.Circle(
        x=lane.end.x,
        y=lane.end.y,
        radius=1.2,
        color=(240, 200, 200, 255),
        batch=batch,
    )
    return (a, b)


def _road_shapes(
    road: Road,
    wait_flags: tuple[bool, bool],
    batch: pyglet.graphics.Batch,
) -> Sequence[pyglet.shapes.ShapeBase]:
    lanes = road.lanes

    lane_a = pyglet.shapes.Line(
        lanes["a"].start.x,
        lanes["a"].start.y,
        lanes["a"].end.x,
        lanes["a"].end.y,
        color=WAIT_LANE_COLOR if wait_flags[0] else DEFAULT_LANE_COLOR,
        batch=batch,
    )
    lane_b = pyglet.shapes.Line(
        lanes["b"].start.x,
        lanes["b"].start.y,
        lanes["b"].end.x,
        lanes["b"].end.y,
        color=WAIT_LANE_COLOR if wait_flags[1] else DEFAULT_LANE_COLOR,
        batch=batch,
    )

    return (
        lane_a,
        lane_b,
        *_node_markers(lanes["a"], batch),
        *_node_markers(lanes["b"], batch),
    )


def _arc_lane_shapes(
    lane: ArcLane, color: tuple[int, int, int, int], batch: pyglet.graphics.Batch
):
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
                color=color,
                batch=batch,
            )
        )
        point = next_point

    return lines


def _arc_shapes(
    arc: Arc,
    wait_flags: tuple[bool, bool],
    batch: pyglet.graphics.Batch,
) -> Sequence[pyglet.shapes.ShapeBase]:
    lane_a = _arc_lane_shapes(
        arc.lanes["a"], WAIT_LANE_COLOR if wait_flags[0] else DEFAULT_LANE_COLOR, batch
    )
    lane_b = _arc_lane_shapes(
        arc.lanes["b"], WAIT_LANE_COLOR if wait_flags[1] else DEFAULT_LANE_COLOR, batch
    )
    return (
        *lane_a,
        *lane_b,
        *_node_markers(arc.lanes["a"], batch),
        *_node_markers(arc.lanes["b"], batch),
    )


def _tee_shapes(
    tee: Tee,
    wait_flags: tuple[bool, bool, bool, bool, bool, bool],
    batch: pyglet.graphics.Batch,
) -> Sequence[pyglet.shapes.ShapeBase]:
    return (
        *_road_shapes(tee.main_road, wait_flags[:2], batch),
        *_arc_shapes(tee.branch_a, wait_flags[2:4], batch),
        *_arc_shapes(tee.branch_b, wait_flags[4:], batch),
    )


class NetworkRenderer:
    def __init__(self, network: Network, wait_flags: WaitFlags | None = None):
        self._junctions: dict[str, Sequence[pyglet.shapes.ShapeBase]] = {}
        self._wait_flags = wait_flags or WaitFlags()
        self._batch: pyglet.graphics.Batch = pyglet.graphics.Batch()
        for junction_label in network.junction_labels():
            junction = network.junction(junction_label)
            self._add_junction(junction_label, junction)

    def draw(self):
        self._batch.draw()

    def _add_junction(self, label: str, junction: Junction):
        match junction:
            case Road():
                self._junctions[label] = _road_shapes(
                    junction,
                    (
                        self._wait_flags[LaneRef(label, junction.LANE_LABELS[0])],
                        self._wait_flags[LaneRef(label, junction.LANE_LABELS[1])],
                    ),
                    self._batch,
                )

            case Arc():
                self._junctions[label] = _arc_shapes(
                    junction,
                    (
                        self._wait_flags[LaneRef(label, junction.LANE_LABELS[0])],
                        self._wait_flags[LaneRef(label, junction.LANE_LABELS[1])],
                    ),
                    self._batch,
                )

            case Tee():
                self._junctions[label] = _tee_shapes(
                    junction,
                    (
                        self._wait_flags[LaneRef(label, junction.LANE_LABELS[0])],
                        self._wait_flags[LaneRef(label, junction.LANE_LABELS[1])],
                        self._wait_flags[LaneRef(label, junction.LANE_LABELS[2])],
                        self._wait_flags[LaneRef(label, junction.LANE_LABELS[3])],
                        self._wait_flags[LaneRef(label, junction.LANE_LABELS[4])],
                        self._wait_flags[LaneRef(label, junction.LANE_LABELS[5])],
                    ),
                    self._batch,
                )
