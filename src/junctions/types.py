import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import ClassVar, Sequence, TypeAlias

from pyglet.math import Vec2


@dataclass(frozen=True)
class PointWithBearing:
    """A point with an associated direction/bearing.

    This is a data type to encapsulate a representation of both where
    a thing is and which direction it's facing.
    """

    point: Vec2
    bearing: float


class Lane(ABC):
    """Represents any kind of lane"""

    @property
    @abstractmethod
    def start(self) -> Vec2:
        raise NotImplementedError()

    @property
    @abstractmethod
    def end(self) -> Vec2:
        raise NotImplementedError()

    @property
    @abstractmethod
    def length(self) -> float:
        raise NotImplementedError()

    @abstractmethod
    def interpolate(self, position: float) -> PointWithBearing:
        """Determine the position and direction of the lane at a given point.

        The position is the distance from the start of the curve, so generally:

            lane.interpolate(0).point == lane.start
            lane.interpolate(lane.length) == lane.end
        """

        raise NotImplementedError()


class StraightLane(Lane):
    def __init__(self, start: Vec2, length: float, bearing: float):
        self._start = start
        self._length = length
        self._bearing = bearing

    @property
    def start(self) -> Vec2:
        return self._start

    @cached_property
    def end(self) -> Vec2:
        return self._start + self.direction * self._length

    @property
    def length(self) -> float:
        return self._length

    @cached_property
    def direction(self) -> Vec2:
        """Direction the lane points in - as unit vector"""
        return Vec2(0, 1).rotate(-self._bearing)

    def interpolate(self, position: float) -> PointWithBearing:
        return PointWithBearing(self._start + self.direction * position, self._bearing)


class ArcLane(Lane):
    def __init__(
        self,
        start: Vec2,
        radius: float,
        start_bearing: float,
        angular_length: float,
        clockwise: bool = True,
    ):
        self._start = start
        self._start_bearing = start_bearing
        self._radius = radius
        self._clockwise = clockwise

        if clockwise:
            start_normal = Vec2(-1, 0).rotate(-start_bearing)
            self._focus = start - start_normal * radius
            end_normal = Vec2(-1, 0).rotate(-start_bearing - angular_length)
        else:
            start_normal = Vec2(1, 0).rotate(-start_bearing)
            self._focus = start - start_normal * radius
            end_normal = Vec2(1, 0).rotate(-start_bearing + angular_length)

        self._end = self._focus + end_normal * radius

        self._length = angular_length * radius

    @property
    def radius(self) -> float:
        return self._radius

    @property
    def focus(self) -> Vec2:
        return self._focus

    @property
    def start(self) -> Vec2:
        return self._start

    @property
    def end(self) -> Vec2:
        return self._end

    @property
    def length(self) -> float:
        return self._length

    def interpolate(self, position: float) -> PointWithBearing:
        angular_position = position / self._radius
        if self._clockwise:
            bearing = self._start_bearing + angular_position
            normal = Vec2(-1, 0).rotate(-bearing)
        else:
            bearing = self._start_bearing - angular_position
            normal = Vec2(1, 0).rotate(-bearing)
        return PointWithBearing(self._focus + normal * self._radius, bearing)


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
        b0 = a0 + Vec2(-self.lane_separation, self.road_length).rotate(-self.bearing)
        return {
            "a": StraightLane(a0, self.road_length, self.bearing),
            "b": StraightLane(b0, self.road_length, self.bearing + math.pi),
        }


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
    def lanes(self) -> dict[str, ArcLane]:
        a0 = Vec2(*self.origin)

        a_lane = ArcLane(
            a0,
            radius=self.arc_radius,
            start_bearing=self.bearing,
            angular_length=self.arc_length,
        )

        b_radius = self.arc_radius + self.lane_separation
        end_normal = Vec2(-1, 0).rotate(-self.bearing - self.arc_length)
        b0 = a_lane.focus + end_normal * b_radius
        b_lane = ArcLane(
            b0,
            radius=b_radius,
            start_bearing=self.bearing + self.arc_length - math.pi,
            angular_length=self.arc_length,
            clockwise=False,
        )
        return {"a": a_lane, "b": b_lane}

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
