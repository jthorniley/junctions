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
    def __init__(self):
        self._storage: MutableMapping[LaneRef, np.ndarray] = defaultdict(
            VehiclePositions._empty_storage
        )
        # Lookup for which lane a vehicle is currently on
        self._vehicle_storage_map: MutableMapping[uuid.UUID, tuple[LaneRef, int]] = {}

    def copy(self) -> VehiclePositions:
        clone = VehiclePositions()
        clone._storage = deepcopy(self._storage)
        clone._vehicle_storage_map = deepcopy(self._vehicle_storage_map)
        return clone

    @staticmethod
    def _empty_storage() -> np.ndarray:
        return np.array([], dtype=[("position", "f4"), ("id", "O")])

    def create_vehicle(self, lane_ref: LaneRef, position: float) -> uuid.UUID:
        storage = self._storage[lane_ref]

        new_id = uuid.uuid4()
        vehicle_index = np.searchsorted(self.positions_by_lane[lane_ref], position)

        updated = np.hstack(
            (
                storage[:vehicle_index],
                np.array([(position, new_id)], dtype=[("position", "f4"), ("id", "O")]),
                storage[vehicle_index:],
            )
        )

        # Bump the indices of all the vehicles after the added one
        for i, vehicle in enumerate(storage[vehicle_index:]["id"]):
            self._vehicle_storage_map[vehicle] = (
                lane_ref,
                int(vehicle_index) + i + 1,
            )

        self._storage[lane_ref] = updated
        self._vehicle_storage_map[new_id] = (lane_ref, int(vehicle_index))

        return new_id

    def switch_lane(self, id: uuid.UUID, lane_ref: LaneRef, position: float) -> None:
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
        return VehiclePositionsByLane(self._storage)

    @property
    def ids_by_lane(self) -> VehicleIdsByLane:
        return VehicleIdsByLane(self._storage)

    def __getitem__(self, id: uuid.UUID) -> VehiclePosition:
        lane_ref, idx = self._vehicle_storage_map[id]
        return VehiclePosition(
            {"lane_ref": lane_ref, "position": self.positions_by_lane[lane_ref][idx]}
        )

    def group_by_lane(self) -> Iterable[tuple[LaneRef, np.ndarray]]:
        return self._storage.items()
