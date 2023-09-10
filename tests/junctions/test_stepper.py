import pytest
from junctions.network import LaneRef, Network
from junctions.state.vehicles import Vehicle, VehiclesState
from junctions.stepper import Stepper
from junctions.types import Road

from tests.junctions.factories import RoadFactory


def test_simple_step():
    # GIVEN a network with one road
    network = Network(default_speed_limit=6.5)
    network.add_junction(RoadFactory.build(), label="theroad")

    # ... and a vehicle on that road
    vehicles = VehiclesState()
    vehicles.add_vehicle(Vehicle(LaneRef("theroad", "a"), 0.0), "v1")

    # ... and a stepper constructed with the network
    stepper = Stepper(network)

    # WHEN I step
    next_vehicle_state = stepper.step(0.1, vehicles)

    # THEN the vehicle has moved
    vehicle = next_vehicle_state.vehicle("v1")
    assert vehicle.lane_ref.junction == "theroad"
    assert vehicle.lane_ref.lane == "a"
    assert vehicle.position == pytest.approx(0.65)


def test_step_to_next_lane():
    # GIVEN a network with two roads and two vehicles
    network = Network(default_speed_limit=10)
    first_road = Road((0, 0), 0, 7, 5)
    second_road = Road((0, 7), 0, 10, 5)

    network.add_junction(first_road, label="first_road")
    # ... Second road has faster speed limit
    network.add_junction(second_road, label="second_road", speed_limit=20)
    # ... Connect the roads together
    network.connect_lanes(LaneRef("first_road", "a"), LaneRef("second_road", "a"))
    network.connect_lanes(LaneRef("second_road", "b"), LaneRef("first_road", "b"))

    # ... first vehicle is traversing the first road
    vehicles = VehiclesState()
    vehicles.add_vehicle(
        Vehicle(LaneRef("first_road", "a"), 0.0), label="first_vehicle"
    )
    # ... second vehicle starts off at the other end on the second-road-b
    vehicles.add_vehicle(
        Vehicle(LaneRef("second_road", "b"), 0.0), label="second_vehicle"
    )

    # WHEN i perform one step
    stepper = Stepper(network)
    vehicles = stepper.step(0.15, vehicles)

    # THEN the vehicles have moved
    first_vehicle = vehicles.vehicle("first_vehicle")
    second_vehicle = vehicles.vehicle("second_vehicle")
    assert first_vehicle.lane_ref.junction == "first_road"
    assert first_vehicle.lane_ref.lane == "a"
    assert first_vehicle.position == pytest.approx(1.5)
    assert second_vehicle.lane_ref.junction == "second_road"
    assert second_vehicle.lane_ref.lane == "b"
    assert second_vehicle.position == pytest.approx(3)

    # WHEN I keep stepping until the second vehicle is past the end of its road
    vehicles = stepper.step(0.15, vehicles)  # position = 6
    vehicles = stepper.step(0.15, vehicles)  # position = 9
    vehicles = stepper.step(0.15, vehicles)  # position ... 12 > 10

    # THEN the first vehicle is still working its way along the slower road
    first_vehicle = vehicles.vehicle("first_vehicle")
    second_vehicle = vehicles.vehicle("second_vehicle")
    assert first_vehicle.lane_ref.junction == "first_road"
    assert first_vehicle.lane_ref.lane == "a"
    assert first_vehicle.position == pytest.approx(6)

    # ... AND the second vehicle has transitioned
    assert second_vehicle.lane_ref.junction == "first_road"
    assert second_vehicle.lane_ref.lane == "b"
    assert second_vehicle.position == pytest.approx(1.0)

    # WHEN we keep going until the first vehicle transitions
    vehicles = stepper.step(0.15, vehicles)

    # ... THEN the first vehicle has transitioned as expected
    first_vehicle = vehicles.vehicle("first_vehicle")
    second_vehicle = vehicles.vehicle("second_vehicle")
    assert first_vehicle.lane_ref.junction == "second_road"
    assert first_vehicle.lane_ref.lane == "a"
    assert first_vehicle.position == pytest.approx(1.0)

    # ... AND the second vehicle continues
    assert second_vehicle.lane_ref.junction == "first_road"
    assert second_vehicle.lane_ref.lane == "b"
    assert second_vehicle.position == pytest.approx(2.5)

    # WHEN we keep going until the vehicles finish
    vehicles = stepper.step(0.15, vehicles)
    vehicles = stepper.step(0.15, vehicles)
    vehicles = stepper.step(0.1, vehicles)
    vehicles = stepper.step(0.1, vehicles)

    with pytest.raises(KeyError):
        first_vehicle = vehicles.vehicle("first_vehicle")

    with pytest.raises(KeyError):
        second_vehicle = vehicles.vehicle("second_vehicle")


def test_stops_if_vehicle_is_in_front():
    # GIVEN a single road with two vehicles
    network = Network(default_speed_limit=10)
    network.add_junction(Road((0, 0), 0, 100, 5))
    vehicles = VehiclesState()
    vehicles.add_vehicle(Vehicle(LaneRef("road1", "a"), 0), label="v1")
    vehicles.add_vehicle(Vehicle(LaneRef("road1", "a"), 4.5), label="v2")

    # WHEN I step
    stepper = Stepper(network)
    vehicles = stepper.step(0.1, vehicles)

    # THEN only the one in front moves
    assert vehicles.vehicle("v1").position == pytest.approx(0.0)
    assert vehicles.vehicle("v2").position == pytest.approx(5.5)

    # now the vehicle is far in front, on the next step both vehicles should move
    vehicles = stepper.step(0.1, vehicles)
    assert vehicles.vehicle("v1").position == pytest.approx(1.0)
    assert vehicles.vehicle("v2").position == pytest.approx(6.5)


def test_stops_if_vehicles_are_on_top():
    # This should be more of an edge case, but if two vehicles get into
    # the exact same position, ONE should move and ONE should stop,
    # so that they get unstuck in a logical way

    network = Network(default_speed_limit=10)
    network.add_junction(Road((0, 0), 0, 100, 5))
    vehicles = VehiclesState()
    vehicles.add_vehicle(Vehicle(LaneRef("road1", "a"), 0), label="v1")
    vehicles.add_vehicle(Vehicle(LaneRef("road1", "a"), 0), label="v2")

    # WHEN I step
    stepper = Stepper(network)
    vehicles = stepper.step(0.1, vehicles)

    # THEN only the one in front moves
    assert vehicles.vehicle("v1").position == pytest.approx(0.0)
    assert vehicles.vehicle("v2").position == pytest.approx(1.0)
