import uuid
from collections import defaultdict
from typing import Mapping, MutableMapping

import numpy as np

from junctions.network import LaneRef


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

    @staticmethod
    def _empty_storage() -> np.ndarray:
        return np.array([], dtype=[("position", "f4"), ("id", "O")])

    def create_vehicle(self, lane_ref: LaneRef, position: float) -> uuid.UUID:
        storage = self._storage[lane_ref]

        new_id = uuid.uuid4()
        updated = np.concatenate([storage, np.array([(0.0, b"")], dtype=storage.dtype)])
        greater = np.argwhere(storage["position"] > position).flatten()

        if greater.shape[0] > 0:
            updated[greater + 1] = updated[greater]
            updated[greater[0]] = (position, new_id)

        else:
            updated[-1] = (position, new_id)

        self._storage[lane_ref] = updated

        return new_id

    @property
    def by_lane(self) -> _VehiclePositionsByLane:
        return _VehiclePositionsByLane(self._storage)

    @property
    def ids_by_lane(self) -> _VehicleIdsByLane:
        return _VehicleIdsByLane(self._storage)
