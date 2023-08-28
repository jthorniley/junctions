from typing import Sequence

from junctions.types import Junction, Lane


class Network:
    def __init__(self, default_speed_limit: float = 9.0):
        self._default_speed_limit = default_speed_limit
        self._junctions: dict[str, Junction] = {}
        self._connected_lanes: dict[tuple[str, str], list[tuple[str, str]]] = {}
        self._lane_speed_limits: dict[tuple[str, str], float] = {}

    def _make_junction_label(self, junction: Junction, label: str | None = None) -> str:
        if label is None:
            cls_name = junction.__class__.__name__.lower()

            i = 1
            for label in self._junctions.keys():
                if label.startswith(cls_name):
                    try:
                        current_value = int(label[len(cls_name) :])
                        i = max(i, current_value + 1)
                    except ValueError:
                        pass

            return f"{cls_name}{i}"

        else:
            if label in self._junctions:
                raise ValueError(f"junction with label {label} already exists")
            return label

    def add_junction(
        self,
        junction: Junction,
        label: str | None = None,
        speed_limit: float | None = None,
    ) -> str:
        label = self._make_junction_label(junction, label)
        self._junctions[label] = junction

        for lane_label in junction.LANE_LABELS:
            self._lane_speed_limits[(label, lane_label)] = (
                self._default_speed_limit if speed_limit is None else speed_limit
            )

        return label

    def junction_labels(self) -> Sequence[str]:
        return tuple(self._junctions.keys())

    def junction(self, junction_label: str) -> Junction:
        return self._junctions[junction_label]

    def lane_labels(self, junction_label: str) -> Sequence[str]:
        junction = self.junction(junction_label)
        return junction.LANE_LABELS

    def lane(self, junction_label: str, lane_label: str) -> Lane:
        """Retrieve a lane by junction and lane label"""
        junction = self.junction(junction_label)
        return junction.lanes[lane_label]

    def connect_lanes(
        self,
        junction_label_1: str,
        lane_label_1: str,
        junction_label_2: str,
        lane_label_2: str,
    ) -> None:
        self._connected_lanes.setdefault((junction_label_1, lane_label_1), []).append(
            (junction_label_2, lane_label_2)
        )

    def connected_lanes(
        self, junction_label: str, lane_label: str
    ) -> Sequence[tuple[str, str]]:
        return tuple(self._connected_lanes.get((junction_label, lane_label), []))

    def speed_limit(self, junction_label: str, lane_label: str) -> float:
        return self._lane_speed_limits[(junction_label, lane_label)]
