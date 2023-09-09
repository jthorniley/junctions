from junctions.network import LaneRef, Network
from junctions.types import Road, Tee


def test_road_has_no_priorities():
    # GIVEN a network
    network = Network()

    # Add a straight road
    network.add_junction(Road((0, 0), 0, 10, 10))

    # THEN there are no priorities defined
    assert network.priority_lanes(LaneRef("road1", "a")) == ()
    assert network.priority_lanes(LaneRef("road1", "b")) == ()


def test_tee_junction_has_priorities():
    # GIVEN a t junction
    network = Network()
    network.add_junction(Tee((0, 0), 0, 10, 4))

    # THEN priorities are defined:
    # Main road lanes no priorities:
    assert network.priority_lanes(LaneRef("tee1", "a")) == ()
    assert network.priority_lanes(LaneRef("tee1", "b")) == ()
    # Right into side road no priorities
    assert network.priority_lanes(LaneRef("tee1", "c")) == ()
    # Left out of side road gives way to main road, left into side road
    assert network.priority_lanes(LaneRef("tee1", "d")) == (
        LaneRef("tee1", "a"),
        LaneRef("tee1", "b"),
        LaneRef("tee1", "f"),
    )
    # Right out of side road gives way to main road right
    assert network.priority_lanes(LaneRef("tee1", "e")) == (LaneRef("tee1", "a"),)
    # Left into side road gives way to main road right, right into side road
    assert network.priority_lanes(LaneRef("tee1", "f")) == (
        LaneRef("tee1", "a"),
        LaneRef("tee1", "c"),
    )
