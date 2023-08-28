from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Literal, Sequence, TypeAlias, TypeGuard


@dataclass(frozen=True)
class InactiveVehicle:
    is_active: Literal[False] = field(default=False, init=False)


@dataclass(frozen=True)
class ActiveVehicle:
    junction_label: str
    lane_label: str
    position: float

    is_active: Literal[True] = field(default=True, init=False)


Vehicle: TypeAlias = InactiveVehicle | ActiveVehicle


def is_active_vehicle(vehicle: Vehicle) -> TypeGuard[ActiveVehicle]:
    return vehicle.is_active


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
                        i = max(i, current_value + 1)
                    except ValueError:
                        pass

            return f"vehicle{i}"

        else:
            if label in self._vehicles:
                raise ValueError(f"vehicle with label {label} already exists")
            return label

    def vehicle_labels(self) -> Sequence[str]:
        return tuple(self._vehicles.keys())

    def vehicle(self, label: str) -> Vehicle:
        return self._vehicles[label]

    def add_vehicle(
        self, vehicle: Vehicle, label: str | None = None
    ) -> tuple[VehiclesState, str]:
        label = self._make_vehicle_label(label)
        new_state = self.with_updates({label: vehicle})
        return new_state, label

    def with_updates(self, updates: dict[str, Vehicle]) -> VehiclesState:
        new_state = VehiclesState()
        new_state._vehicles = self._vehicles.copy()
        new_state._vehicles.update(updates)
        return new_state

    def items(self) -> Iterable[tuple[str, Vehicle]]:
        return self._vehicles.items()
