import math

from junctions.network import LaneRef, Network
from junctions.priority_wait import priority_wait
from junctions.state.vehicles import Vehicle, VehiclesState
from junctions.types import Road, Tee


def simple_t_junction_network():
    network = Network()
    network.add_junction(Road((0, 0), 0, 100, 5), label="main_road_1")
    network.add_junction(Tee((0, 100), 0, 20, 5), label="tee")
    network.add_junction(Road((0, 120), 0, 100, 5), label="main_road_2")
    network.add_junction(Road((5, 105), math.pi / 2, 100, 5), label="side_road")
    return network


def test_no_wait_flags_for_no_vehicles():
    # Given a network
    network = simple_t_junction_network()

    # and no vehicles
    vehicles = VehiclesState()

    # WHEN i calculate wait flags
    wait_flags = priority_wait(network, vehicles)

    # THEN none are set
    for lane in network.all_lanes():
        assert not wait_flags[lane]


def test_wait_on_t_junction():
    # GIVEN network
    network = simple_t_junction_network()

    # AND vehicle on the main road of the t-junction
    vehicles = VehiclesState()
    vehicles.add_vehicle(Vehicle(LaneRef("tee", "a"), 1))

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
    vehicles = VehiclesState()
    vehicles.add_vehicle(Vehicle(LaneRef("tee", "f"), 1))
    vehicles.add_vehicle(Vehicle(LaneRef("tee", "f"), 2))

    # WHEN I calculate wait flags
    wait_flags = priority_wait(network, vehicles)

    # THEN the left turn out of side road lane waits
    assert wait_flags[LaneRef("tee", "d")]
    assert not wait_flags[LaneRef("tee", "e")]
    assert not wait_flags[LaneRef("tee", "f")]
    assert not wait_flags[LaneRef("tee", "a")]
    assert not wait_flags[LaneRef("tee", "b")]
    assert not wait_flags[LaneRef("tee", "c")]
