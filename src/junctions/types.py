from dataclasses import dataclass

from pyglet.math import Vec2


@dataclass
class Road:
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

    origin: Vec2
    bearing: float
    road_length: float
    lane_separation: float
