import pytest
from junctions.types import Arc, Road

from tests.junctions.factories import ArcFactory, RoadFactory


@pytest.mark.parametrize("_fuzz", range(20))  # implicitly 20 random seeds
def test_road_length(_fuzz):
    # GIVEN a road
    road: Road = RoadFactory.build()

    # WHEN I calculate either lane's length``
    lane_a, lane_b = road.lanes.values()

    # THEN they are equal to the road length
    assert lane_a.length == pytest.approx(road.road_length)
    assert lane_b.length == pytest.approx(road.road_length)


@pytest.mark.parametrize("_fuzz", range(20))  # implicitly 20 random seeds
def test_arc_length(_fuzz):
    # GIVEN a arc
    arc: Arc = ArcFactory.build()

    # WHEN I calculate the lane lengths
    lane_a, lane_b = arc.lanes.values()

    # THEN lane a is always the inner lane:
    assert lane_a.length == pytest.approx(arc.arc_radius * arc.arc_length)
    # ... lane b is the outer lane
    assert lane_b.length == pytest.approx(
        (arc.arc_radius + arc.lane_separation) * arc.arc_length
    )
