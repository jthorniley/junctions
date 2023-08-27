import math
from dataclasses import dataclass
from functools import cached_property
from typing import ClassVar, Sequence, TypeAlias

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

    LANE_LABELS: ClassVar[Sequence[str]] = ("a", "b")

    origin: tuple[float, float]
    bearing: float
    road_length: float
    lane_separation: float

    @cached_property
    def lanes(self) -> dict[str, Lane]:
        """Road lanes, A then B"""
        a0 = Vec2(*self.origin)
        course = Vec2(0, self.road_length).rotate(-self.bearing)
        a1 = a0 + course
        separation = Vec2(-self.lane_separation, 0).rotate(-self.bearing)
        b0 = a1 + separation
        b1 = a0 + separation

        return {"a": Lane(a0, a1), "b": Lane(b0, b1)}


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

    LANE_LABELS: ClassVar[Sequence[str]] = ("a", "b")

    origin: tuple[float, float]
    bearing: float
    arc_length: float
    arc_radius: float
    lane_separation: float

    @cached_property
    def lanes(self) -> dict[str, Lane]:
        a0 = Vec2(*self.origin)
        origin_normal = Vec2(-1, 0).rotate(-self.bearing)
        end_normal = Vec2(-1, 0).rotate(-self.bearing - self.arc_length)

        return {
            "a": Lane(a0, self.focus + end_normal * self.arc_radius),
            "b": Lane(
                self.focus + end_normal * (self.arc_radius + self.lane_separation),
                self.focus + origin_normal * (self.arc_radius + self.lane_separation),
            ),
        }

    @cached_property
    def focus(self) -> Vec2:
        a0 = Vec2(*self.origin)
        origin_normal = Vec2(-1, 0).rotate(-self.bearing)
        return a0 - origin_normal * self.arc_radius


@dataclass(frozen=True)
class Tee:
    """A T-Junction which is a composite of a straight road and two arcs that allow
    diverting to or from a side road at right angles.

    Parameters:
        origin: origin of the main road
        bearing: bearing of the main road
        main_road_length: length of the main road section that is within the junction
        lane_separation: lane separation on both roads

    The parameters of the components are constrained by the above.
    """

    LANE_LABELS: ClassVar[Sequence[str]] = ("a", "b", "c", "d", "e", "f")

    origin: tuple[float, float]
    main_road_bearing: float
    main_road_length: float
    lane_separation: float

    @cached_property
    def main_road(self) -> Road:
        return Road(
            self.origin,
            self.main_road_bearing,
            self.main_road_length,
            self.lane_separation,
        )

    @cached_property
    def branch_a(self) -> Arc:
        return Arc(
            origin=self.origin,
            bearing=self.main_road_bearing,
            arc_length=math.pi / 2,
            arc_radius=(self.main_road_length - self.lane_separation) / 2,
            lane_separation=self.lane_separation,
        )

    @cached_property
    def branch_b(self) -> Arc:
        return Arc(
            origin=(*self.branch_a.lanes["b"].start,),
            bearing=self.main_road_bearing - math.pi / 2,
            arc_length=math.pi / 2,
            arc_radius=self.branch_a.arc_radius,
            lane_separation=self.lane_separation,
        )

    @cached_property
    def lanes(self) -> dict[str, Lane]:
        return {
            "a": self.main_road.lanes["a"],
            "b": self.main_road.lanes["b"],
            "c": self.branch_a.lanes["a"],
            "d": self.branch_a.lanes["b"],
            "e": self.branch_b.lanes["a"],
            "f": self.branch_b.lanes["b"],
        }


Junction: TypeAlias = Road | Arc | Tee
