import numpy as np

from ..types import Lane, Point2, Road


def create_road(origin: Point2, road_length: float, lane_separation: float) -> Road:
    """Create a single road as initial example - going "east-west" (i.e. along the x
    direction).

    ![](images/a-b.png)
    """
    a0 = origin
    a1 = origin + np.array([0, road_length])
    b1 = a0 + np.array([lane_separation, 0])
    b0 = b1 + np.array([0, road_length])

    return Road(a=Lane(start=a0, end=a1), b=Lane(start=b0, end=b1))
