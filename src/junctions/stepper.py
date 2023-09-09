from __future__ import annotations

import random
from typing import TYPE_CHECKING

from junctions.network import LaneRef
from junctions.priority_wait import priority_wait
from junctions.state.vehicles import (
    Vehicle,
    VehiclesState,
)
from junctions.state.wait_flags import WaitFlags

if TYPE_CHECKING:
    from junctions.network import Network


class Stepper:
    """Utility for stepping the simulation in time"""

    def __init__(self, network: Network):
        self._network = network
        self._wait_flags: WaitFlags | None = None
        self._vehicle_planned_next_lane: dict[str, LaneRef] = {}

    def _calculate_vehicle_update(
        self, dt: float, vehicle_label: str, vehicle: Vehicle
    ) -> Vehicle | None:
        # the algorithm is defined in doc/03-vehicles.md
        speed = self._network.speed_limit(vehicle.lane_ref)
        movement = speed * dt

        next_position = vehicle.position + movement

        lane = self._network.lane(vehicle.lane_ref)

        if (excess := next_position - lane.length) > 0:
            next_lane_ref = None

            if vehicle_label in self._vehicle_planned_next_lane:
                next_lane_ref = self._vehicle_planned_next_lane[vehicle_label]
            else:
                next_lane_choices = self._network.connected_lanes(vehicle.lane_ref)

                if next_lane_choices:
                    next_lane_ref = random.choice(next_lane_choices)
                    self._vehicle_planned_next_lane[vehicle_label] = next_lane_ref

            if next_lane_ref:
                if self._wait_flags and self._wait_flags[next_lane_ref]:
                    # Next lane is wait, set vehicle to end of current lane
                    return Vehicle(lane_ref=vehicle.lane_ref, position=lane.length)
                else:
                    t_excess = excess / speed

                    next_lane_speed_limit = self._network.speed_limit(next_lane_ref)

                    try:
                        self._vehicle_planned_next_lane.pop(vehicle_label)
                    except KeyError:
                        ...

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

        self._wait_flags = priority_wait(self._network, vehicles_state)

        next_vehicles_state = VehiclesState()

        for vehicle_label, vehicle in vehicles_state.items():
            next_vehicle = self._calculate_vehicle_update(dt, vehicle_label, vehicle)
            if next_vehicle is not None:
                next_vehicles_state.add_vehicle(next_vehicle, vehicle_label)

        return next_vehicles_state

    @property
    def wait_flags(self) -> WaitFlags | None:
        return self._wait_flags
