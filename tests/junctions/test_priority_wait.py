import math

import pytest
from junctions.network import LaneRef, Network
from junctions.priority_wait import priority_wait
from junctions.state.vehicles import _Vehicle, _VehiclesState
from junctions.types import Road, Tee


def simple_t_junction_network():
    network = Network()
    network.add_junction(Road((0, 0), 0, 100, 5), label="main_road_1", speed_limit=4)
    network.add_junction(Tee((0, 100), 0, 20, 5), label="tee", speed_limit=2)
    network.add_junction(Road((0, 120), 0, 100, 5), label="main_road_2", speed_limit=4)
    network.add_junction(
        Road((5, 105), math.pi / 2, 100, 5), label="side_road", speed_limit=4
    )
    network.connect_lanes(LaneRef("main_road_1", "a"), LaneRef("tee", "a"))
    network.connect_lanes(LaneRef("main_road_1", "a"), LaneRef("tee", "c"))
    network.connect_lanes(LaneRef("tee", "a"), LaneRef("main_road_2", "a"))
    network.connect_lanes(LaneRef("tee", "b"), LaneRef("main_road_1", "b"))
    network.connect_lanes(LaneRef("tee", "c"), LaneRef("side_road", "a"))
    network.connect_lanes(LaneRef("tee", "d"), LaneRef("main_road_1", "b"))
    network.connect_lanes(LaneRef("tee", "e"), LaneRef("main_road_2", "a"))
    network.connect_lanes(LaneRef("tee", "f"), LaneRef("side_road", "a"))
    network.connect_lanes(LaneRef("main_road_2", "b"), LaneRef("tee", "b"))
    network.connect_lanes(LaneRef("main_road_2", "b"), LaneRef("tee", "f"))
    network.connect_lanes(LaneRef("side_road", "b"), LaneRef("tee", "d"))
    network.connect_lanes(LaneRef("side_road", "b"), LaneRef("tee", "e"))
    return network


def test_no_wait_flags_for_no_vehicles():
    # Given a network
    network = simple_t_junction_network()

    # and no vehicles
    vehicles = _VehiclesState()

    # WHEN i calculate wait flags
    wait_flags = priority_wait(network, vehicles)

    # THEN none are set
    for lane in network.all_lanes():
        assert not wait_flags[lane]


def test_wait_on_t_junction():
    # GIVEN network
    network = simple_t_junction_network()

    # AND vehicle on the main road of the t-junction
    vehicles = _VehiclesState()
    vehicles.add_vehicle(_Vehicle(LaneRef("tee", "a"), 1))

    # WHEN I calculate wait flags
    wait_flags = priority_wait(network, vehicles)

    # THEN the lanes crossing the main road get a wait flag
    assert wait_flags[LaneRef("tee", "d")]
    assert wait_flags[LaneRef("tee", "e")]
    assert wait_flags[LaneRef("tee", "f")]
    assert not wait_flags[LaneRef("tee", "a")]
    assert not wait_flags[LaneRef("tee", "b")]
    assert not wait_flags[LaneRef("tee", "c")]


def test_two_vehicles_on_t_junction():
    # GIVEN network
    network = simple_t_junction_network()

    # AND two vehicles turning left
    vehicles = _VehiclesState()
    vehicles.add_vehicle(_Vehicle(LaneRef("tee", "f"), 1))
    vehicles.add_vehicle(_Vehicle(LaneRef("tee", "f"), 2))

    # WHEN I calculate wait flags
    wait_flags = priority_wait(network, vehicles)

    # THEN the left turn out of side road lane waits
    assert wait_flags[LaneRef("tee", "d")]
    assert not wait_flags[LaneRef("tee", "e")]
    assert not wait_flags[LaneRef("tee", "f")]
    assert not wait_flags[LaneRef("tee", "a")]
    assert not wait_flags[LaneRef("tee", "b")]
    assert not wait_flags[LaneRef("tee", "c")]


def test_vehicle_on_feeder_lane():
    # GIVEN a network
    network = simple_t_junction_network()

    # The turn radius on the t junction are these
    large_turn_length = 6.25 * math.pi
    small_turn_length = 3.75 * math.pi
    assert network.lane(LaneRef("tee", "d")).length == pytest.approx(large_turn_length)
    assert network.lane(LaneRef("tee", "c")).length == pytest.approx(small_turn_length)

    # AND a vehicle on the main road that feeds the t junction
    # it is within the large turn clear time, but not the small turn clear time
    # note the main road goes twice the speed of the junction, so need twice
    # the runway to avoid collision
    vehicles = _VehiclesState()
    vehicles.add_vehicle(
        _Vehicle(LaneRef("main_road_1", "a"), position=100 - large_turn_length * 2 + 1)
    )

    # WHEN i calculate the wait flags
    wait_flags = priority_wait(network, vehicles)

    # THEN the large radius turn lanes are waiting, the small radius one is not
    assert wait_flags[LaneRef("tee", "d")]
    assert not wait_flags[LaneRef("tee", "e")]
    assert wait_flags[LaneRef("tee", "f")]
    assert not wait_flags[LaneRef("tee", "a")]
    assert not wait_flags[LaneRef("tee", "b")]
    assert not wait_flags[LaneRef("tee", "c")]

    # Same thing, but with vehicle a bit closer, small turn also waits
    vehicles = _VehiclesState()
    vehicles.add_vehicle(
        _Vehicle(LaneRef("main_road_1", "a"), position=100 - small_turn_length * 2 + 1)
    )

    # WHEN i calculate the wait flags
    wait_flags = priority_wait(network, vehicles)

    # THEN the large radius turn lanes are waiting, the small radius one is not
    assert wait_flags[LaneRef("tee", "d")]
    assert wait_flags[LaneRef("tee", "e")]
    assert wait_flags[LaneRef("tee", "f")]
    assert not wait_flags[LaneRef("tee", "a")]
    assert not wait_flags[LaneRef("tee", "b")]
    assert not wait_flags[LaneRef("tee", "c")]

    # Feeder vehicle further away, lanes not blocked
    vehicles = _VehiclesState()
    vehicles.add_vehicle(
        _Vehicle(LaneRef("main_road_1", "a"), position=100 - large_turn_length * 2 - 1)
    )

    # WHEN i calculate the wait flags
    wait_flags = priority_wait(network, vehicles)

    # THEN the large radius turn lanes are waiting, the small radius one is not
    assert not wait_flags[LaneRef("tee", "d")]
    assert not wait_flags[LaneRef("tee", "e")]
    assert not wait_flags[LaneRef("tee", "f")]
    assert not wait_flags[LaneRef("tee", "a")]
    assert not wait_flags[LaneRef("tee", "b")]
    assert not wait_flags[LaneRef("tee", "c")]
