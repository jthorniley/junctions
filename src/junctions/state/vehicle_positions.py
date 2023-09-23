from __future__ import annotations

import uuid
from collections import defaultdict
from copy import deepcopy
from typing import Iterable, Mapping, MutableMapping, TypedDict

import numpy as np

from junctions.network import LaneRef


class VehiclePosition(TypedDict):
    lane_ref: LaneRef
    position: float


class VehiclePositionsByLane:
    def __init__(self, storage: Mapping[LaneRef, np.ndarray]) -> None:
        self._storage = storage

    def __getitem__(self, lane_ref: LaneRef) -> np.ndarray:
        return self._storage[lane_ref]["position"]


class VehicleIdsByLane:
    def __init__(self, storage: Mapping[LaneRef, np.ndarray]) -> None:
        self._storage = storage

    def __getitem__(self, lane_ref: LaneRef) -> np.ndarray:
        return self._storage[lane_ref]["id"]


class VehiclePositions:
    """Stores the current state of vehicles in the simulation.

    Each vehicle is on a lane (referenced by a LaneRef object) and has a position
    from the start of that lane.
    """

    def __init__(self):
        # Internally, there are two storages - this one is indexed by LaneRef,
        # returning a numpy structured array containing ids and positions for
        # all the vehicles on that lane. See _empty_storage() for the code
        # that creates the empty structured array.
        #
        # Importantly, the structured array is always sorted by ascending order
        # of position, which makes various aspects of iterating through the
        # vehicles (for solving the sim) more efficient.
        self._storage: MutableMapping[LaneRef, np.ndarray] = defaultdict(
            VehiclePositions._empty_storage
        )
        # Second, we maintain an index by vehicle ID, which is useful for quickly
        # finding where a vehicle is when the ID is already known. (This is
        # generally less useful in simulation stepping, where what we need to
        # do is iterate all vehicles on all lanes)
        self._vehicle_storage_map: MutableMapping[uuid.UUID, tuple[LaneRef, int]] = {}

    def copy(self) -> VehiclePositions:
        # make a deep clone of the storage data and return it
        clone = VehiclePositions()
        clone._storage = deepcopy(self._storage)
        clone._vehicle_storage_map = deepcopy(self._vehicle_storage_map)
        return clone

    @staticmethod
    def _empty_storage() -> np.ndarray:
        return np.array([], dtype=[("position", "f4"), ("id", "O")])

    def create_vehicle(self, lane_ref: LaneRef, position: float) -> uuid.UUID:
        # insert a new vehicle
        storage = self._storage[lane_ref]

        new_id = uuid.uuid4()

        # we have to be careful to insert it at the right place...
        vehicle_index = np.searchsorted(self.positions_by_lane[lane_ref], position)

        updated = np.hstack(
            (
                storage[:vehicle_index],
                np.array([(position, new_id)], dtype=[("position", "f4"), ("id", "O")]),
                storage[vehicle_index:],
            )
        )

        # and since the vehicle could have been inserted in the middle, we have
        # to make sure we correct the indices of the by-id lookup to reflect that
        for i, vehicle in enumerate(storage[vehicle_index:]["id"]):
            self._vehicle_storage_map[vehicle] = (
                lane_ref,
                int(vehicle_index) + i + 1,
            )

        # now set the storage data
        self._storage[lane_ref] = updated

        # and insert the reverse lookup into the index
        self._vehicle_storage_map[new_id] = (lane_ref, int(vehicle_index))

        return new_id

    def switch_lane(self, id: uuid.UUID, lane_ref: LaneRef, position: float) -> None:
        # move vehicle from wherever it currently is to a new lane ref/position
        old_lane_ref, old_index = self._vehicle_storage_map[id]

        # Update the old lane
        old_storage = self._storage[old_lane_ref]
        for i, vehicle in enumerate(old_storage[old_index + 1 :]["id"]):
            self._vehicle_storage_map[vehicle] = (
                old_lane_ref,
                old_index + i,
            )
        old_storage = np.hstack((old_storage[:old_index], old_storage[old_index + 1 :]))
        self._storage[old_lane_ref] = old_storage

        # Add to new lane
        new_vehicle_index = int(
            np.searchsorted(self.positions_by_lane[lane_ref], position)
        )
        new_storage = self._storage[lane_ref]

        new_storage = np.hstack(
            (
                new_storage[:new_vehicle_index],
                np.array([(position, id)], dtype=[("position", "f4"), ("id", "O")]),
                new_storage[new_vehicle_index:],
            )
        )

        # Bump the indices of all the vehicles after the added one
        for i, vehicle in enumerate(new_storage[new_vehicle_index + 1 :]["id"]):
            self._vehicle_storage_map[vehicle] = (
                lane_ref,
                new_vehicle_index + i + 1,
            )

        self._vehicle_storage_map[id] = (lane_ref, new_vehicle_index)

        self._storage[lane_ref] = new_storage

    def remove(self, id: uuid.UUID) -> None:
        old_lane_ref, old_index = self._vehicle_storage_map[id]

        del self._vehicle_storage_map[id]

        for i, (_, id) in enumerate(self._storage[old_lane_ref][old_index + 1 :]):
            self._vehicle_storage_map[id] = (old_lane_ref, old_index + i)

        self._storage[old_lane_ref] = np.hstack(
            (
                self._storage[old_lane_ref][:old_index],
                self._storage[old_lane_ref][old_index + 1 :],
            )
        )

    @property
    def positions_by_lane(self) -> VehiclePositionsByLane:
        """Use this to access all the vehicle positions on a given lane.

        For example:

            >>> positions.positions_by_lane[lane_ref]

        This returns the positions of the vehicles on the specified
        lane _in ascending order_. It is important if the vehicle
        positions are modified that the order is not changed. To change
        the position of a vehicle while guaranteeing that the ordering
        is not broken use switch_lane().
        """
        return VehiclePositionsByLane(self._storage)

    @property
    def ids_by_lane(self) -> VehicleIdsByLane:
        """Return the IDs of the vehicles on a given lane.

        For example:

            >>> positions.ids_by_lane[lane_ref]

        The resulting numpy array of IDs (each of which is a `uuid.UUID`)
        is the vehicle IDs on the specified lane.

        The result is a view onto internal storage used by this
        class. DO NOT change the elements of the returned array as
        the storage state will become inconsistent.
        """
        return VehicleIdsByLane(self._storage)

    def __getitem__(self, id: uuid.UUID) -> VehiclePosition:
        """For retricing the vehicle lane/position by vehicle ID"""
        lane_ref, idx = self._vehicle_storage_map[id]
        return VehiclePosition(
            {"lane_ref": lane_ref, "position": self.positions_by_lane[lane_ref][idx]}
        )

    def group_by_lane(self) -> Iterable[tuple[LaneRef, np.ndarray]]:
        """Iterate all the vehicles in the system, grouped by lane."""
        return self._storage.items()
