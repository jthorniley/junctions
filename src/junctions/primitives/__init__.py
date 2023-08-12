import numpy as np

from ..types import Lane, Point2, Road


def create_road(
    origin: Point2, road_length: float, lane_separation: float, bearing: float = 0
) -> Road:
    """Create a single road.

    The origin is the start of the A lane. The B lane will be separated by
    `lane_separation` meters. The `road_length` is the length of the lanes.

    `bearing` is the angle north that the A lane travels:

    * 0 -> A runs south-north (towards +ve y)
    * PI/2 -> A runs east-west (towards +ve x)
    * PI -> A runs north-south (towards -ve y)
    * etc

    ![](images/a-b.png)
    """

    rotation_matrix = np.array(
        [[np.cos(bearing), np.sin(bearing)], [-np.sin(bearing), np.cos(bearing)]]
    )
    a0 = origin
    a1 = origin + np.matmul(rotation_matrix, np.array([0, road_length]))
    b1 = a0 + np.matmul(rotation_matrix, np.array([lane_separation, 0]))
    b0 = b1 + np.matmul(rotation_matrix, np.array([0, road_length]))

    return Road(a=Lane(start=a0, end=a1), b=Lane(start=b0, end=b1))
