from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

import pyglet
from junctions.state.vehicles import (
    ActiveVehicle,
    Vehicle,
    VehiclesState,
    is_active_vehicle,
)

if TYPE_CHECKING:
    from junctions.network import Network


def _vehicle_shapes(
    vehicle: ActiveVehicle, network: Network, batch: pyglet.graphics.Batch
) -> Sequence[pyglet.shapes.ShapeBase]:
    lane = network.lane(vehicle.junction_label, vehicle.lane_label)
    pos = lane.interpolate(vehicle.position)
    return [
        pyglet.shapes.Circle(
            pos.point.x,
            pos.point.y,
            radius=2.5,
            segments=10,
            color=(200, 0, 0, 255),
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
