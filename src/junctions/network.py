from types import MappingProxyType
from typing import Mapping, Sequence

from junctions.types import Junction


class Network:
    def __init__(self):
        self._junctions: dict[str, Junction] = {}

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

    def junction(self, label: str) -> Junction:
        return self._junctions[label]

    def all_junctions(self) -> Sequence[Junction]:
        return tuple(self._junctions.values())

    @property
    def junction_lookup(self) -> Mapping[str, Junction]:
        # immutable view
        return MappingProxyType(self._junctions)
