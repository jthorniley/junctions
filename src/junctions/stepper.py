from __future__ import annotations

import random
import uuid
from typing import TYPE_CHECKING, Final

import numpy as np

from junctions.network import LaneRef
from junctions.priority_wait import priority_wait
from junctions.state.vehicle_positions import VehiclePositions
from junctions.state.wait_flags import WaitFlags

if TYPE_CHECKING:
    from junctions.network import Network

VEHICLE_SEPARATION_LIMIT: Final = 5


class Stepper:
    """Utility for stepping the simulation in time"""

    def __init__(self, network: Network, vehicle_positions: VehiclePositions) -> None:
        self._network = network
        self._vehicle_positions = vehicle_positions
        self._wait_flags: WaitFlags | None = None
        self._next_lane_choice: dict[uuid.UUID, LaneRef] = {}

    @property
    def wait_flags(self) -> WaitFlags | None:
        return self._wait_flags

    def _next_lane_ref(
        self, lane_ref: LaneRef, vehicle_id: uuid.UUID
    ) -> LaneRef | None:
        if vehicle_id in self._next_lane_choice:
            # next lane already chosen on a previous step, use that one
            return self._next_lane_choice[vehicle_id]
        next_lane_choices = self._network.connected_lanes(lane_ref)

        if next_lane_choices:
            next_lane_ref = random.choice(next_lane_choices)
            self._next_lane_choice[vehicle_id] = next_lane_ref
            return next_lane_ref
        return None

    def step(self, dt: float) -> None:
        """Perform a step with time interval dt"""

        self._wait_flags = priority_wait(self._network, self._vehicle_positions)

        for lane_ref, vehicle_data in self._vehicle_positions.group_by_lane():
            speed_limit = self._network.speed_limit(lane_ref)

            position = vehicle_data["position"]
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
                vehicle_id = id[vehicle_index]

                # Pick lane that vehicle leaving this lane should move to
                next_lane_ref = self._next_lane_ref(lane_ref, vehicle_id)

                if next_lane_ref:
                    if self._wait_flags[next_lane_ref]:
                        # Vehicle is stuck on the end of its current lane, no switch
                        next_vehicle_positions.by_lane[lane_ref][
                            vehicle_index
                        ] = lane_length
                    else:
                        # move vehicle to next lane, clear stored lane choice
                        del self._next_lane_choice[vehicle_id]
                        speed_limit = self._network.speed_limit(lane_ref)
                        excess = position[vehicle_index] - lane_length
                        t_excess = excess / speed_limit

                        next_lane_speed_limit = self._network.speed_limit(next_lane_ref)

                        next_vehicle_positions.switch_lane(
                            vehicle_id,
                            next_lane_ref,
                            t_excess * next_lane_speed_limit,
                        )
                else:
                    next_vehicle_positions.remove(vehicle_id)

        self._vehicle_positions._storage = next_vehicle_positions._storage
        self._vehicle_positions._vehicle_storage_map = (
            next_vehicle_positions._vehicle_storage_map
        )
