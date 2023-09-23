from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Sequence

import pyglet
from junctions.network import LaneRef
from junctions.state.vehicle_positions import VehiclePositions
from pyglet.math import Vec2

if TYPE_CHECKING:
    from junctions.network import Network


def _vehicle_shapes(
    vehicle: float, lane_ref: LaneRef, network: Network, batch: pyglet.graphics.Batch
) -> Sequence[pyglet.shapes.ShapeBase]:
    lane = network.lane(lane_ref)
    pos = lane.interpolate(vehicle)

    forward = Vec2(0, 1).rotate(-pos.bearing)
    right = Vec2(-1, 0).rotate(-pos.bearing)
    a = pos.point + right * 0.5
    b = a - forward * 4
    c = b + right * 2
    d = c + forward * 4
    return [
        pyglet.shapes.Polygon(
            (a[0], a[1]),
            (b[0], b[1]),
            (c[0], c[1]),
            (d[0], d[1]),
            (a[0], a[1]),
            color=(10, 240, 20, 255),
            batch=batch,
        )
    ]


class VehiclesStateRenderer:
    def __init__(self, network: Network, vehicles_state: VehiclePositions):
        self._network = network
        self._vehicles: dict[str, Sequence[pyglet.shapes.ShapeBase]] = {}
        self._batch: pyglet.graphics.Batch = pyglet.graphics.Batch()

        for lane in network.all_lanes():
            for id, vehicle in zip(
                vehicles_state.ids_by_lane[lane], vehicles_state.by_lane[lane]
            ):
                self._add_vehicle(id, lane, vehicle)

    def draw(self):
        self._batch.draw()

    def _add_vehicle(self, id: uuid.UUID, lane: LaneRef, vehicle: float):
        self._vehicles[str(id)] = _vehicle_shapes(
            vehicle, lane, self._network, self._batch
        )
