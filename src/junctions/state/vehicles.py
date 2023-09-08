from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from junctions.network import LaneRef


@dataclass(frozen=True)
class Vehicle:
    lane_ref: LaneRef
    position: float


class VehiclesState:
    """State object for vehicles."""

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

    def add_vehicle(self, vehicle: Vehicle, label: str | None = None) -> None:
        label = self._make_vehicle_label(label)
        self._vehicles[label] = vehicle

    def items(self) -> Iterable[tuple[str, Vehicle]]:
        return self._vehicles.items()
