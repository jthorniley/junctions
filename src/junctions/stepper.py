from __future__ import annotations

import random
from typing import TYPE_CHECKING

from junctions.state.vehicles import (
    Vehicle,
    VehiclesState,
)

if TYPE_CHECKING:
    from junctions.network import Network


class Stepper:
    """Utility for stepping the simulation in time"""

    def __init__(self, network: Network):
        self._network = network

    def _calculate_vehicle_update(self, dt: float, vehicle: Vehicle) -> Vehicle | None:
        # the algorithm is defined in doc/03-vehicles.md
        speed = self._network.speed_limit(vehicle.lane_ref)
        movement = speed * dt

        next_position = vehicle.position + movement

        lane = self._network.lane(vehicle.lane_ref)

        if (excess := next_position - lane.length) > 0:
            t_excess = excess / speed

            next_lane_choices = self._network.connected_lanes(vehicle.lane_ref)

            if next_lane_choices:
                next_lane_ref = random.choice(next_lane_choices)

                next_lane_speed_limit = self._network.speed_limit(next_lane_ref)

                return Vehicle(
                    lane_ref=next_lane_ref,
                    position=t_excess * next_lane_speed_limit,
                )

            else:
                return None
        else:
            return Vehicle(
                lane_ref=vehicle.lane_ref,
                position=next_position,
            )

    def step(self, dt: float, vehicles_state: VehiclesState) -> VehiclesState:
        """Perform a step with time interval dt"""

        next_vehicles_state = VehiclesState()

        for vehicle_label, vehicle in vehicles_state.items():
            next_vehicle = self._calculate_vehicle_update(dt, vehicle)
            if next_vehicle is not None:
                next_vehicles_state.add_vehicle(next_vehicle, vehicle_label)

        return next_vehicles_state
