from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

import pyglet
from junctions.state.vehicles import (
    ActiveVehicle,
    Vehicle,
    VehiclesState,
    is_active_vehicle,
)
from pyglet.math import Vec2

if TYPE_CHECKING:
    from junctions.network import Network


def _vehicle_shapes(
    vehicle: ActiveVehicle, network: Network, batch: pyglet.graphics.Batch
) -> Sequence[pyglet.shapes.ShapeBase]:
    lane = network.lane(vehicle.junction_label, vehicle.lane_label)
    pos = lane.interpolate(vehicle.position)

    forward = Vec2(0, 1).rotate(-pos.bearing)
    right = Vec2(-1, 0).rotate(-pos.bearing)
    a = pos.point + right * 0.5
    b = a - forward * 3
    c = b + right * 1.5
    d = c + forward * 3
    return [
        pyglet.shapes.Polygon(
            (a[0], a[1]),
            (b[0], b[1]),
            (c[0], c[1]),
            (d[0], d[1]),
            (a[0], a[1]),
            color=(200, 200, 200, 255),
            batch=batch,
        )
    ]


class VehiclesStateRenderer:
    def __init__(self, network: Network, vehicles_state: VehiclesState):
        self._network = network
        self._vehicles: dict[str, Sequence[pyglet.shapes.ShapeBase]] = {}
        self._batch: pyglet.graphics.Batch = pyglet.graphics.Batch()

        for label, vehicle in vehicles_state.items():
            self._add_vehicle(label, vehicle)

    def draw(self):
        self._batch.draw()

    def _add_vehicle(self, label: str, vehicle: Vehicle):
        if not is_active_vehicle(vehicle):
            self._vehicles[label] = ()
            return

        self._vehicles[label] = _vehicle_shapes(vehicle, self._network, self._batch)
