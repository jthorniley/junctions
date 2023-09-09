from dataclasses import dataclass
from typing import Iterable, Sequence

from junctions.types import Junction, Lane


@dataclass(frozen=True)
class LaneRef:
    """Reference a lane by labels (junction/lane)"""

    junction: str
    lane: str


class Network:
    def __init__(self, default_speed_limit: float = 9.0):
        self._default_speed_limit = default_speed_limit
        self._junctions: dict[str, Junction] = {}
        self._connected_lanes: dict[LaneRef, list[LaneRef]] = {}
        self._lane_speed_limits: dict[LaneRef, float] = {}

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
            self._lane_speed_limits[LaneRef(label, lane_label)] = (
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

    def lane(self, lane_ref: LaneRef) -> Lane:
        """Retrieve a lane by junction and lane label"""
        junction = self.junction(lane_ref.junction)
        return junction.lanes[lane_ref.lane]

    def connect_lanes(self, lane_ref_1: LaneRef, lane_ref_2: LaneRef) -> None:
        self._connected_lanes.setdefault(lane_ref_1, []).append(lane_ref_2)

    def connected_lanes(self, lane_ref: LaneRef) -> Sequence[LaneRef]:
        return tuple(self._connected_lanes.get(lane_ref, []))

    def speed_limit(self, lane_ref: LaneRef) -> float:
        return self._lane_speed_limits[lane_ref]

    def priority_lanes(self, lane_ref: LaneRef) -> Sequence[LaneRef]:
        junc = self.junction(lane_ref.junction)
        return tuple(
            LaneRef(lane_ref.junction, lane)
            for lane in junc.priority_over_lane(lane_ref.lane)
        )

    def all_lanes(self) -> Iterable[LaneRef]:
        for junction_label, junction in self._junctions.items():
            for lane_label in junction.lanes.keys():
                yield LaneRef(junction_label, lane_label)
