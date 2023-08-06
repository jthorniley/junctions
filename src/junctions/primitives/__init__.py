import numpy as np

from ..types import Lane, Point2, Road


def create_road(origin: Point2, road_length: float, lane_separation: float) -> Road:
    """Create a single road as initial example - going "east-west" (i.e. along the x
    direction).

    ![](images/a-b.png)
    """
    a0 = origin
    a1 = origin + np.array([road_length, 0])
    b1 = a0 + np.array([0, lane_separation])
    b0 = b1 + np.array([road_length, 0])

    return Road(a=Lane(start=a0, end=a1), b=Lane(start=b0, end=b1))
