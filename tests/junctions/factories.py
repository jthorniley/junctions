import math

from factory import Factory, LazyFunction
from factory.random import randgen
from junctions.types import Arc, Road, Tee


class RoadFactory(Factory):
    class Meta:
        model = Road

    origin = LazyFunction(
        lambda: (randgen.random() * 100 + 50, randgen.random() * 100 + 50)
    )
    bearing = LazyFunction(lambda: (randgen.random() * 2 * math.pi))
    road_length = LazyFunction(lambda: (randgen.random() * 100 + 30))
    lane_separation = LazyFunction(lambda: (randgen.random() * 5 + 3))


class ArcFactory(Factory):
    class Meta:
        model = Arc

    origin = LazyFunction(
        lambda: (randgen.random() * 100 + 50, randgen.random() * 100 + 50)
    )
    bearing = LazyFunction(lambda: (randgen.random() * math.pi))
    arc_length = LazyFunction(lambda: (randgen.random() * math.pi))
    arc_radius = LazyFunction(lambda: (randgen.random() * 10 + 3))
    lane_separation = LazyFunction(lambda: (randgen.random() * 5 + 3))


class TeeFactory(Factory):
    class Meta:
        model = Tee

    origin = LazyFunction(
        lambda: (randgen.random() * 100 + 50, randgen.random() * 100 + 50)
    )
    main_road_bearing = LazyFunction(lambda: (randgen.random() * math.pi))
    main_road_length = LazyFunction(lambda: (randgen.random() * 100 + 30))
    lane_separation = LazyFunction(lambda: (randgen.random() * 5 + 3))
