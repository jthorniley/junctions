import math

import pytest
from junctions.network import Network
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
            # target point on the other side
            NotConnected((20, 10)),
        ],
    )

    assert not proposal.can_commit
    proposed_road: Road = proposal.junction
    assert proposed_road.origin == (pytest.approx(-10), pytest.approx(-10))
    assert proposed_road.road_length == pytest.approx(0)
    assert proposed_road.bearing == pytest.approx(math.pi * 1.25)
    assert proposed_road.lane_separation == pytest.approx(5)
