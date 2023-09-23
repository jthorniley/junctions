from __future__ import annotations

import random
from collections import defaultdict
from operator import itemgetter
from typing import TYPE_CHECKING, Final

import numpy as np

from junctions.network import LaneRef
from junctions.priority_wait import priority_wait
from junctions.state.vehicle_positions import VehiclePositions
from junctions.state.vehicles import (
    _Vehicle,
    _VehiclesState,
)
from junctions.state.wait_flags import WaitFlags

if TYPE_CHECKING:
    from junctions.network import Network

VEHICLE_SEPARATION_LIMIT: Final = 5


class Stepper:
    """Utility for stepping the simulation in time"""

    def __init__(self, network: Network, vehicle_positions: VehiclePositions) -> None:
        self._network = network
        self._vehicle_positions = vehicle_positions

    def _next_lane_ref(self, lane_ref: LaneRef) -> LaneRef | None:
        next_lane_choices = self._network.connected_lanes(lane_ref)

        if next_lane_choices:
            next_lane_ref = random.choice(next_lane_choices)
            return next_lane_ref
        return None

    def step(self, dt: float) -> None:
        """Perform a step with time interval dt"""

        for lane_ref in self._network.all_lanes():
            speed_limit = self._network.speed_limit(lane_ref)

            position = self._vehicle_positions.by_lane[lane_ref]
            movement = np.ones_like(position) * dt * speed_limit

            gap = np.diff(position)

            movement[:-1][gap < VEHICLE_SEPARATION_LIMIT] = 0

            position[:] += movement

        next_vehicle_positions = self._vehicle_positions.copy()

        for lane_ref in self._network.all_lanes():
            position = self._vehicle_positions.by_lane[lane_ref]
            id = self._vehicle_positions.ids_by_lane[lane_ref]
            lane_length = self._network.lane(lane_ref).length
            # Index where the vehicles are past the lane end
            lane_end_index = np.searchsorted(position, lane_length)

            for vehicle_index in range(lane_end_index, position.shape[0]):
                # Pick lane that vehicle leaving this lane should move to
                next_lane_ref = self._next_lane_ref(lane_ref)

                if next_lane_ref:
                    speed_limit = self._network.speed_limit(lane_ref)
                    excess = position[vehicle_index] - lane_length
                    t_excess = excess / speed_limit

                    next_lane_speed_limit = self._network.speed_limit(next_lane_ref)

                    next_vehicle_positions.switch_lane(
                        id[vehicle_index],
                        next_lane_ref,
                        t_excess * next_lane_speed_limit,
                    )
                else:
                    next_vehicle_positions.remove(id[vehicle_index])

        self._vehicle_positions._storage = next_vehicle_positions._storage
        self._vehicle_positions._vehicle_storage_map = (
            next_vehicle_positions._vehicle_storage_map
        )

    # def __init__(self, network: Network):
    #     self._network = network
    #     self._wait_flags: WaitFlags | None = None
    #     self._vehicle_planned_next_lane: dict[str, LaneRef] = {}

    # def _calculate_vehicle_update(
    #     self, dt: float, vehicle_label: str, vehicle: _Vehicle
    # ) -> _Vehicle | None:
    #     # the algorithm is defined in doc/03-vehicles.md
    #     speed = self._network.speed_limit(vehicle.lane_ref)
    #     movement = speed * dt

    #     next_position = vehicle.position + movement

    #     lane = self._network.lane(vehicle.lane_ref)

    #     if (excess := next_position - lane.length) > 0:
    #         next_lane_ref = None

    #         if vehicle_label in self._vehicle_planned_next_lane:
    #             next_lane_ref = self._vehicle_planned_next_lane[vehicle_label]
    #         else:
    #             next_lane_choices = self._network.connected_lanes(vehicle.lane_ref)

    #             if next_lane_choices:
    #                 next_lane_ref = random.choice(next_lane_choices)
    #                 self._vehicle_planned_next_lane[vehicle_label] = next_lane_ref

    #         if next_lane_ref:
    #             if self._wait_flags and self._wait_flags[next_lane_ref]:
    #                 # Next lane is wait, set vehicle to end of current lane
    #                 return _Vehicle(lane_ref=vehicle.lane_ref, position=lane.length)
    #             else:
    #                 t_excess = excess / speed

    #                 next_lane_speed_limit = self._network.speed_limit(next_lane_ref)

    #                 try:
    #                     self._vehicle_planned_next_lane.pop(vehicle_label)
    #                 except KeyError:
    #                     ...

    #                 return _Vehicle(
    #                     lane_ref=next_lane_ref,
    #                     position=t_excess * next_lane_speed_limit,
    #                 )

    #         else:
    #             return None
    #     else:
    #         return _Vehicle(
    #             lane_ref=vehicle.lane_ref,
    #             position=next_position,
    #         )

    # def step(self, dt: float, vehicles_state: _VehiclesState) -> _VehiclesState:
    #     """Perform a step with time interval dt"""

    #     self._wait_flags = priority_wait(self._network, vehicles_state)

    #     next_vehicles_state = _VehiclesState()

    #     lane_vehicle_map: defaultdict[LaneRef, list[tuple[str, float]]] = defaultdict(
    #         list
    #     )
    #     for vehicle_label, vehicle in vehicles_state.items():
    #         lane_vehicle_map[vehicle.lane_ref].append((vehicle_label, vehicle.position))

    #     for _, vehicles in lane_vehicle_map.items():
    #         vehicles.sort(key=itemgetter(1))

    #     for lane_ref, lane_vehicles in lane_vehicle_map.items():
    #         for vehicle_index, (vehicle_label, vehicle_position) in enumerate(
    #             lane_vehicles
    #         ):
    #             if vehicle_index < len(lane_vehicles) - 1:
    #                 next_vehicle_position = lane_vehicles[vehicle_index + 1][1]
    #                 if next_vehicle_position < (
    #                     vehicle_position + VEHICLE_SEPARATION_LIMIT
    #                 ):
    #                     next_vehicles_state.add_vehicle(
    #                         _Vehicle(lane_ref, vehicle_position), vehicle_label
    #                     )
    #                     continue

    #             next_vehicle = self._calculate_vehicle_update(
    #                 dt, vehicle_label, _Vehicle(lane_ref, vehicle_position)
    #             )
    #             if next_vehicle is not None:
    #                 next_vehicles_state.add_vehicle(next_vehicle, vehicle_label)

    #     return next_vehicles_state

    # @property
    # def wait_flags(self) -> WaitFlags | None:
    #     return self._wait_flags
