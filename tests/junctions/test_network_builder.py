from pickletools import pyset

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
            ConnectTerminal(Terminal.DOWN, Terminal.UP, "road1"),
            NotConnected(Terminal.UP, (0, 130)),
        ],
    )

    assert proposal.can_commit
    proposed_road: Road = proposal.junction
    assert proposed_road.origin == (pytest.approx(0), pytest.approx(100))
    assert proposed_road.road_length == pytest.approx(30)
    assert proposed_road.bearing == pytest.approx(0)
    assert proposed_road.lane_separation == pytest.approx(5)
