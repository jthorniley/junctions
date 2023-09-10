import numpy as np

from junctions.network import LaneRef


class VehiclePositions:
    def __init__(self):
        self._position_storage: dict[LaneRef, np.ndarray] = {}

    def __getitem__(self, lane_ref: LaneRef) -> np.ndarray:
        return self._position_storage.get(lane_ref, np.array([]))

    def create_vehicle(self, lane_ref: LaneRef, position: float):
        storage = self._position_storage.setdefault(lane_ref, np.array([]))

        updated = np.concatenate([storage[:], [0.0]])
        greater = np.argwhere(storage > position).flatten()
        if greater.shape[0] > 0:
            updated[greater + 1] = updated[greater]
            updated[greater[0]] = position
        else:
            updated[-1] = position

        self._position_storage[lane_ref] = updated
