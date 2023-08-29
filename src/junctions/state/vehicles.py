from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Vehicle:
    junction_label: str
    lane_label: str
    position: float


class VehiclesState:
    """State object for vehicles.

    State is designed to be immutable, so any changes make a new copy of the state.
    This helps to ensure consistent state and state updates.
    """

    def __init__(self):
        self._vehicles: dict[str, Vehicle] = {}

    def _make_vehicle_label(self, label: str | None) -> str:
        if label is None:
            i = 1
            for label in self._vehicles.keys():
                if label.startswith("vehicle"):
                    try:
                        current_value = int(label[len("vehicle") :])
                    except ValueError:
                        pass
                    else:
                        i = max(i, current_value + 1)

            return f"vehicle{i}"

        else:
            if label in self._vehicles:
                raise ValueError(f"vehicle with label {label} already exists")
            return label

    def vehicle_labels(self) -> Iterable[str]:
        return self._vehicles.keys()

    def vehicle(self, label: str) -> Vehicle:
        return self._vehicles[label]

    def add_vehicle(self, vehicle: Vehicle, label: str | None = None) -> VehiclesState:
        label = self._make_vehicle_label(label)
        new_state = self.with_updates({label: vehicle})
        return new_state

    def with_updates(self, updates: dict[str, Vehicle | None]) -> VehiclesState:
        new_state = VehiclesState()
        new_state._vehicles = self._vehicles.copy()
        for label, vehicle in updates.items():
            if vehicle is None:
                del new_state._vehicles[label]
            else:
                new_state._vehicles[label] = vehicle
        return new_state

    def items(self) -> Iterable[tuple[str, Vehicle]]:
        return self._vehicles.items()
