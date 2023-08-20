from dataclasses import dataclass
from functools import cached_property
from typing import TypeAlias

from pyglet.math import Vec2


@dataclass(frozen=True)
class Lane:
    start: Vec2
    end: Vec2


@dataclass(frozen=True)
class Road:
    """Create a single road.

    The origin is the start of the A lane. The B lane will be separated by
    `lane_separation` meters. The `road_length` is the length of the lanes.

    `bearing` is the angle north that the A lane travels:

    * 0 -> A runs south-north (towards +ve y)
    * PI/2 -> A runs west-east (towards +ve x)
    * PI -> A runs north-south (towards -ve y)
    * etc

    ![](images/a-b.png)
    """

    origin: tuple[float, float]
    bearing: float
    road_length: float
    lane_separation: float

    @cached_property
    def lanes(self) -> tuple[Lane, Lane]:
        """Road lanes, A then B"""
        a0 = Vec2(*self.origin)
        course = Vec2(0, self.road_length).rotate(-self.bearing)
        a1 = a0 + course
        separation = Vec2(-self.lane_separation, 0).rotate(-self.bearing)
        b0 = a1 + separation
        b1 = a0 + separation

        return (Lane(a0, a1), Lane(b0, b1))


@dataclass(frozen=True)
class Arc:
    """Two lane road following an arc curve.

    Two lanes (A and B) follow a circular arc.

    A starts at `origin` with given `bearing`.

    B is parallel to A but runs in the opposite direction. The
    `lane_separation` defines the distance between B and A.

    `arc_radius` defines the curvature radius for the inner (A) lane.

    The `arc_length` is how far A curves around which can be from
    `0` to `2*PI` (negative values not allowed).

    The A lane is always the "inner" lane of the curve, and "B" the
    outer.

    ![](images/arc.png)
    """

    origin: tuple[float, float]
    bearing: float
    arc_length: float
    arc_radius: float
    lane_separation: float

    @cached_property
    def lanes(self) -> tuple[Lane, Lane]:
        a0 = Vec2(*self.origin)
        origin_normal = Vec2(-1, 0).rotate(-self.bearing)
        end_normal = Vec2(-1, 0).rotate(-self.bearing - self.arc_length)

        return (
            Lane(a0, self.focus + end_normal * self.arc_radius),
            Lane(
                self.focus + end_normal * (self.arc_radius + self.lane_separation),
                self.focus + origin_normal * (self.arc_radius + self.lane_separation),
            ),
        )

    @cached_property
    def focus(self) -> Vec2:
        a0 = Vec2(*self.origin)
        origin_normal = Vec2(-1, 0).rotate(-self.bearing)
        return a0 - origin_normal * self.arc_radius


Junction: TypeAlias = Road | Arc
