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
    vehicles = VehiclesState().add_vehicle(Vehicle(LaneRef("theroad", "a"), 0.0), "v1")

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

    # ... first vehicle is traverising the first road
    vehicles = (
        VehiclesState().add_vehicle(
            Vehicle(LaneRef("first_road", "a"), 0.0), label="first_vehicle"
        )
        # ... second vehicle starts off at the other end on the second-road-b
        .add_vehicle(Vehicle(LaneRef("second_road", "b"), 0.0), label="second_vehicle")
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
