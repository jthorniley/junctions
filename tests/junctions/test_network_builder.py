import math

import pytest
from junctions.network import LaneRef, Network
from junctions.network_builder import (
    ConnectTerminal,
    NetworkBuilder,
    NotConnected,
    Terminal,
)
from junctions.types import Road


def test_add_road_to_existing():
    """
    GIVEN one road in the network
    WHEN I propose another one in line with the existing
    THEN the proposal is valid
    """
    network = Network()
    network_builder = NetworkBuilder(network)

    network.add_junction(Road((0, 0), 0, 100, 5), label="road1")

    proposal = network_builder.propose(
        Road,
        [
            ConnectTerminal(Terminal.UP, "road1"),
            NotConnected((0, 130)),
        ],
    )

    assert proposal.can_commit
    proposed_road: Road = proposal.junction
    assert proposed_road.origin == (pytest.approx(0), pytest.approx(100))
    assert proposed_road.road_length == pytest.approx(30)
    assert proposed_road.bearing == pytest.approx(0)
    assert proposed_road.lane_separation == pytest.approx(5)


def test_add_road_to_existing_reverse():
    """
    As add_road_to_existing, but the connections can be specified in reverse order
    (does not affect result)

    GIVEN one road in the network
    WHEN I propose another one in line with the existing
    THEN the proposal is valid
    """
    network = Network()
    network_builder = NetworkBuilder(network)

    network.add_junction(Road((0, 0), 0, 100, 5), label="road1")

    proposal = network_builder.propose(
        Road,
        [
            NotConnected((0, 130)),
            ConnectTerminal(Terminal.UP, "road1"),
        ],
    )

    assert proposal.can_commit
    proposed_road: Road = proposal.junction
    assert proposed_road.origin == (pytest.approx(0), pytest.approx(100))
    assert proposed_road.road_length == pytest.approx(30)
    assert proposed_road.bearing == pytest.approx(0)
    assert proposed_road.lane_separation == pytest.approx(5)


def test_add_road_keeps_angle():
    """
    GIVEN one road in the network
    WHEN I propose another one
    AND the new proposed end point is not on the same bearing as the initial road
    THEN the initial road bearing is useds
    """
    network = Network()
    network_builder = NetworkBuilder(network)

    # road bearing south-west
    network.add_junction(
        Road((0, 0), math.pi * 1.25, math.sqrt(2) * 10, 5), label="road1"
    )

    assert network.junction("road1").lanes["a"].end.x == pytest.approx(-10)
    assert network.junction("road1").lanes["a"].end.y == pytest.approx(-10)

    proposal = network_builder.propose(
        Road,
        [
            ConnectTerminal(Terminal.UP, "road1"),
            # target point not directly in line
            NotConnected((-20, -10)),
        ],
    )

    assert proposal.can_commit
    proposed_road: Road = proposal.junction
    assert proposed_road.origin == (pytest.approx(-10), pytest.approx(-10))
    assert proposed_road.road_length == pytest.approx(math.sqrt(50))
    assert proposed_road.bearing == pytest.approx(math.pi * 1.25)
    assert proposed_road.lane_separation == pytest.approx(5)
    assert proposed_road.lanes["a"].end.x == pytest.approx(-15)
    assert proposed_road.lanes["a"].end.y == pytest.approx(-15)


def test_add_road_keeps_angle_to_down_terminal():
    """
    GIVEN one road in the network
    WHEN I propose another one
    AND I connect the new one to the DOWN terminal of the existing one
    AND the new proposed end point is not on the same bearing as the initial road
    THEN the initial road bearing is useds
    """
    network = Network()
    network_builder = NetworkBuilder(network)

    # road bearing south-west
    network.add_junction(
        Road((0, 0), math.pi * 1.25, math.sqrt(2) * 10, 5), label="road1"
    )

    proposal = network_builder.propose(
        Road,
        [
            ConnectTerminal(Terminal.DOWN, "road1"),
            # target point not directly in line
            NotConnected((5, 5)),
        ],
    )

    assert proposal.can_commit
    proposed_road: Road = proposal.junction
    assert proposed_road.origin == (
        pytest.approx(3.5355339059327),
        pytest.approx(-3.5355339059327),
    )
    assert proposed_road.road_length == pytest.approx(math.sqrt(50))
    assert proposed_road.bearing == pytest.approx(math.pi * 0.25)
    assert proposed_road.lane_separation == pytest.approx(5)
    assert proposed_road.lanes["b"].start.x == pytest.approx(5)
    assert proposed_road.lanes["b"].start.y == pytest.approx(5)


def test_add_road_cannot_turn_back():
    """
    GIVEN one road in the network
    WHEN I propose another one
    AND the new proposed end point would require the new road to run
        in the opposite direction to the original road
    THEN we don't get a valid road
    """
    network = Network()
    network_builder = NetworkBuilder(network)

    # road bearing south-west
    network.add_junction(
        Road((0, 0), math.pi * 1.25, math.sqrt(2) * 10, 5), label="road1"
    )

    assert network.junction("road1").lanes["a"].end.x == pytest.approx(-10)
    assert network.junction("road1").lanes["a"].end.y == pytest.approx(-10)

    proposal = network_builder.propose(
        Road,
        [
            ConnectTerminal(Terminal.UP, "road1"),
            # target point (just) on the other side
            NotConnected((-9.9, -9)),
        ],
    )

    assert not proposal.can_commit
    proposed_road: Road = proposal.junction
    assert proposed_road.origin == (pytest.approx(-10), pytest.approx(-10))
    assert proposed_road.road_length == pytest.approx(0)
    assert proposed_road.bearing == pytest.approx(math.pi * 1.25)
    assert proposed_road.lane_separation == pytest.approx(5)


def test_add_and_commit_road_with_no_constraints():
    """
    WHEN I propose a valid road with no connections
    THEN I can add it to the network by committing it
    """

    network = Network()
    network_builder = NetworkBuilder(network)

    # connect 10,30 to 100,30 - so length 90 and bearing PI/2
    network_builder.propose(
        Road, [NotConnected((10, 30)), NotConnected((100, 30))]
    ).commit("road1")

    # Assert: should exist
    committed = network.junction("road1")
    assert isinstance(committed, Road)
    # ... values as expected
    assert committed.origin == (10, 30)
    assert committed.lane_separation == 5  # this is just a random default
    assert committed.road_length == 90
    assert committed.bearing == math.pi / 2


def test_connect_roads():
    """
    GIVEN a network with a road in already
    WHEN I propose and commit another road
    THEN suitable connections are created in the network
    """

    network = Network()
    network_builder = NetworkBuilder(network)

    # connect 10,30 to 100,30 - so length 90 and bearing PI/2
    network_builder.propose(
        Road, [NotConnected((10, 30)), NotConnected((100, 30))]
    ).commit("road1")
    network_builder.propose(
        Road, [ConnectTerminal(Terminal.UP, "road1"), NotConnected((150, 30))]
    ).commit("road2")

    # Assert: should exist
    road1_committed = network.junction("road1")
    assert isinstance(road1_committed, Road)
    road2_committed = network.junction("road2")
    assert isinstance(road2_committed, Road)

    # connections have been made
    assert network.connected_lanes(LaneRef("road1", "a")) == (LaneRef("road2", "a"),)
    assert network.connected_lanes(LaneRef("road2", "b")) == (LaneRef("road1", "b"),)

    # check that the junction positions make sense for the connections
    assert (
        network.lane(LaneRef("road1", "a")).end
        - network.lane(LaneRef("road2", "a")).start
    ).mag == pytest.approx(0)
    assert (
        network.lane(LaneRef("road2", "b")).end
        - network.lane(LaneRef("road1", "b")).start
    ).mag == pytest.approx(0)


def test_connect_road_to_down_terminal():
    """
    Like test_connect_roads, but connect to the down terminal rather than the UP
    terminal of the existing road.

    GIVEN a network with a road in already
    WHEN I propose and commit another road
    THEN suitable connections are created in the network
         - the original roads b lane connects to our b-lane
    """

    network = Network()
    network_builder = NetworkBuilder(network)

    # connect 10,30 to 100,30 - so length 90 and bearing PI/2
    network_builder.propose(
        Road, [NotConnected((10, 30)), NotConnected((100, 30))]
    ).commit("road1")
    network_builder.propose(
        Road, [ConnectTerminal(Terminal.DOWN, "road1"), NotConnected((0, 30))]
    ).commit("road2")

    # Assert: should exist
    road1_committed = network.junction("road1")
    assert isinstance(road1_committed, Road)
    road2_committed = network.junction("road2")
    assert isinstance(road2_committed, Road)

    # connections have been made
    assert network.connected_lanes(LaneRef("road1", "b")) == (LaneRef("road2", "a"),)
    assert network.connected_lanes(LaneRef("road2", "b")) == (LaneRef("road1", "a"),)
    # check that the junction positions make sense for the connections
    assert (
        network.lane(LaneRef("road1", "b")).end
        - network.lane(LaneRef("road2", "a")).start
    ).mag == pytest.approx(0)
    assert (
        network.lane(LaneRef("road2", "b")).end
        - network.lane(LaneRef("road1", "a")).start
    ).mag == pytest.approx(0)
