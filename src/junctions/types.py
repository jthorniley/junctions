from dataclasses import dataclass
from typing import TypeAlias

import numpy as np
from numpy.typing import NDArray

Point2: TypeAlias = NDArray[np.float32]


@dataclass
class Lane:
    start: Point2
    end: Point2


@dataclass
class Road:
    a: Lane
    b: Lane
