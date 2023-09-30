from __future__ import annotations

import random
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

import numpy as np

from junctions.network import LaneRef
from junctions.priority_wait import priority_wait
from junctions.state.vehicle_positions import VehiclePositions
from junctions.state.wait_flags import WaitFlags

if TYPE_CHECKING:
    from junctions.network import Network

VEHICLE_SEPARATION_LIMIT: Final = 5


@dataclass
class LaneChange:
    id: uuid.UUID
    lane_ref: LaneRef
    position: float


@dataclass
class RemoveVehicle:
    id: uuid.UUID


class Stepper:
    """Utility for stepping the simulation in time


    The algorithm is defined in doc/03-vehicles.md
    """

    def __init__(self, network: Network, vehicle_positions: VehiclePositions) -> None:
        self._network = network
        self._vehicle_positions = vehicle_positions
        self._wait_flags: WaitFlags | None = None
        self._next_lane_choice: dict[uuid.UUID, LaneRef] = {}

    @property
    def wait_flags(self) -> WaitFlags | None:
        return self._wait_flags

    def _move_vehicles(self, dt: float):
        """Move all the vehicles according to the speed limit of the lane
        they are on. Stop if they are blocked by a vehicle in front or a wait flag.
        """
        for lane_ref, vehicle_data in self._vehicle_positions.group_by_lane():
            speed_limit = self._network.speed_limit(lane_ref)

            position = vehicle_data["position"]
            movement = np.ones_like(position) * dt * speed_limit

            gap = np.diff(position)

            movement[:-1][gap < VEHICLE_SEPARATION_LIMIT] = 0

            position[:] += movement

    def _calculate_lane_changes(self) -> list[LaneChange | RemoveVehicle]:
        """For vehicles that have moved past the end of their current lane,
        decide where to move them. The options are:

        * Choose a new lane at random
        * If there is no follow-on lane, remove the vehicle from the sim
        * If the next lane is clear (no wait flag) move onto it
        * If the next lane has a wait flag, stop at the end of current lane

        We return a list of changes to make as a set to be applied after all
        changes have been calculated. This allows us to modify the storage
        in-place and not have a copy, but avoid modifying the state during
        the initial iteration which could cause inconsistent calculations.

        """
        changes = []

        for lane_ref, vehicle_data in self._vehicle_positions.group_by_lane():
            # iterator each lane (lane_ref) and the vehicles on that lane
            id = vehicle_data["id"]
            position = vehicle_data["position"]
            lane_length = self._network.lane(lane_ref).length

            # Index where the vehicles are past the lane end - the lane data is
            # sorted so vehicles after this index are past the end
            lane_end_index = np.searchsorted(position, lane_length)

            for vehicle_index in range(lane_end_index, position.shape[0]):
                vehicle_id = id[vehicle_index]

                # Pick lane that vehicle leaving this lane should move to
                next_lane_ref = self._choose_new_lane(lane_ref, vehicle_id)

                if next_lane_ref:
                    if self._wait_flags and self._wait_flags[next_lane_ref]:
                        # Vehicle is stuck on the end of its current lane, no switch
                        changes.append(LaneChange(vehicle_id, lane_ref, lane_length))
                    else:
                        # move vehicle to next lane, clear stored lane choice
                        del self._next_lane_choice[vehicle_id]
                        speed_limit = self._network.speed_limit(lane_ref)
                        excess = position[vehicle_index] - lane_length
                        t_excess = excess / speed_limit

                        next_lane_speed_limit = self._network.speed_limit(next_lane_ref)

                        changes.append(
                            LaneChange(
                                vehicle_id,
                                next_lane_ref,
                                t_excess * next_lane_speed_limit,
                            )
                        )
                else:
                    changes.append(RemoveVehicle(vehicle_id))

        return changes

    def _choose_new_lane(
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

        self._move_vehicles(dt)

        # lane switches needed
        for change in self._calculate_lane_changes():
            match change:
                case LaneChange(vehicle_id, lane_ref, position):
                    self._vehicle_positions.switch_lane(vehicle_id, lane_ref, position)

                case RemoveVehicle(vehicle_id):
                    self._vehicle_positions.remove(vehicle_id)
