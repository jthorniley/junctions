import uuid
from collections import defaultdict
from typing import Mapping, MutableMapping, TypedDict

import numpy as np

from junctions.network import LaneRef


class VehiclePosition(TypedDict):
    lane_ref: LaneRef
    position: float


class _VehiclePositionsByLane:
    def __init__(self, storage: Mapping[LaneRef, np.ndarray]) -> None:
        self._storage = storage

    def __getitem__(self, lane_ref: LaneRef) -> np.ndarray:
        return self._storage[lane_ref]["position"]


class _VehicleIdsByLane:
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

    @staticmethod
    def _empty_storage() -> np.ndarray:
        return np.array([], dtype=[("position", "f4"), ("id", "O")])

    def create_vehicle(self, lane_ref: LaneRef, position: float) -> uuid.UUID:
        storage = self._storage[lane_ref]

        new_id = uuid.uuid4()
        vehicle_index = np.searchsorted(self.by_lane[lane_ref], position)

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
                i + 1,
            )

        self._storage[lane_ref] = updated
        self._vehicle_storage_map[new_id] = (lane_ref, int(vehicle_index))

        return new_id

    def switch_lane(self, id: uuid.UUID, lane_ref: LaneRef, position: float) -> None:
        ...

    @property
    def by_lane(self) -> _VehiclePositionsByLane:
        return _VehiclePositionsByLane(self._storage)

    @property
    def ids_by_lane(self) -> _VehicleIdsByLane:
        return _VehicleIdsByLane(self._storage)

    def __getitem__(self, id: uuid.UUID) -> VehiclePosition:
        lane_ref, idx = self._vehicle_storage_map[id]
        return VehiclePosition(
            {"lane_ref": lane_ref, "position": self.by_lane[lane_ref][idx]}
        )
