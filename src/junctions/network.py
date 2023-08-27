from typing import Sequence

from junctions.types import Junction, Lane


class Network:
    def __init__(self):
        self._junctions: dict[str, Junction] = {}
        self._connected_lanes: dict[tuple[str, str], list[tuple[str, str]]] = {}

    def add_junction(self, junction: Junction, label: str | None = None) -> str:
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

            label = f"{cls_name}{i}"
            self._junctions[label] = junction
            return label

        else:
            if label in self._junctions:
                raise ValueError(f"junction with label {label} already exists")
            self._junctions[label] = junction
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
