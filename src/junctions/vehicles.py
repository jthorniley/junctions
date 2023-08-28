from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Literal, Sequence, TypeAlias, TypeGuard


@dataclass
class InactiveVehicle:
    is_active: Literal[False] = field(default=False, init=False)


@dataclass
class ActiveVehicle:
    junction_label: str
    lane_label: str
    position: float

    is_active: Literal[True] = field(default=True, init=False)


Vehicle: TypeAlias = InactiveVehicle | ActiveVehicle


def is_active_vehicle(vehicle: Vehicle) -> TypeGuard[ActiveVehicle]:
    return vehicle.is_active


class Vehicles:
    """Represents the state of vehicles on a network."""

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

    def add_vehicle(self, label: str | None = None) -> str:
        """Add a vehicle to the system.

        Initially the vehicle is in an inactive state and won't actually
        perform any state updates.
        """
        label = self._make_vehicle_label(label)
        self._vehicles[label] = InactiveVehicle()
        return label

    def move_to_lane_start(
        self, vehicle_label: str, junction_label: str, lane_label: str
    ) -> None:
        """Move the specified vehicle on to the start of the given lane and activate it.

        After calling this, the vehicle should move with state updates.
        """
        self._vehicles[vehicle_label] = ActiveVehicle(junction_label, lane_label, 0)

    def deactivate(self, vehicle_label: str):
        """Deactivate the vehicle (remove it from the simulation)"""
        self._vehicles[vehicle_label] = InactiveVehicle()

    def vehicle_labels(self) -> Sequence[str]:
        return tuple(self._vehicles.keys())

    def vehicle(self, label: str) -> Vehicle:
        return self._vehicles[label]

    def items(self) -> Iterable[tuple[str, Vehicle]]:
        """dict-like iterator over all vehicles"""
        return self._vehicles.items()
