import pytest
from junctions.network import Network
from junctions.stepper import Stepper
from junctions.types import Road
from junctions.vehicles import Vehicle, Vehicles, is_active_vehicle

from tests.junctions.factories import RoadFactory


def test_simple_step():
    # GIVEN a network with one road
    network = Network(default_speed_limit=6.5)
    network.add_junction(RoadFactory.build(), label="theroad")
    vehicles = Vehicles()
    vehicles.add_vehicle("thevehicle")
    vehicles.move_to_lane_start("thevehicle", "theroad", "a")

    # ... and a stepper constructed with the vehicles and network
    stepper = Stepper(network, vehicles)

    # WHEN I step
    stepper.step(0.1)

    # THEN the vehicle has moved
    vehicle = vehicles.vehicle("thevehicle")
    assert is_active_vehicle(vehicle)
    assert vehicle.junction_label == "theroad"
    assert vehicle.lane_label == "a"
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
    network.connect_lanes("first_road", "a", "second_road", "a")
    network.connect_lanes("second_road", "b", "first_road", "b")

    # ... first vehicle is traverising the first road
    vehicles = Vehicles()
    vehicles.add_vehicle("first_vehicle")
    vehicles.move_to_lane_start("first_vehicle", "first_road", "a")
    # ... second vehicle starts off at the other end on the second-road-b
    vehicles.add_vehicle("second_vehicle")
    vehicles.move_to_lane_start("second_vehicle", "second_road", "b")

    # WHEN i perform one step
    stepper = Stepper(network, vehicles)
    stepper.step(0.15)

    # THEN the vehicles have moved
    first_vehicle = vehicles.vehicle("first_vehicle")
    second_vehicle = vehicles.vehicle("second_vehicle")
    assert is_active_vehicle(first_vehicle)
    assert is_active_vehicle(second_vehicle)
    assert first_vehicle.junction_label == "first_road"
    assert first_vehicle.lane_label == "a"
    assert first_vehicle.position == pytest.approx(1.5)
    assert second_vehicle.junction_label == "second_road"
    assert second_vehicle.lane_label == "b"
    assert second_vehicle.position == pytest.approx(3)

    # WHEN I keep stepping until the second vehicle is past the end of its road
    stepper.step(0.15)  # position = 6
    stepper.step(0.15)  # position = 9
    stepper.step(0.15)  # position ... 12 > 10

    # THEN the first vehicle is still working its way along the slower road
    first_vehicle = vehicles.vehicle("first_vehicle")
    second_vehicle = vehicles.vehicle("second_vehicle")
    assert is_active_vehicle(first_vehicle)
    assert is_active_vehicle(second_vehicle)
    assert first_vehicle.junction_label == "first_road"
    assert first_vehicle.lane_label == "a"
    assert first_vehicle.position == pytest.approx(6)

    # ... AND the second vehicle has transitioned
    assert second_vehicle.junction_label == "first_road"
    assert second_vehicle.lane_label == "b"
    assert second_vehicle.position == pytest.approx(1.0)

    # WHEN we keep going until the first vehicle transitions
    stepper.step(0.15)

    # ... THEN the first vehicle has transitioned as expected
    first_vehicle = vehicles.vehicle("first_vehicle")
    second_vehicle = vehicles.vehicle("second_vehicle")
    assert is_active_vehicle(first_vehicle)
    assert is_active_vehicle(second_vehicle)
    assert first_vehicle.junction_label == "second_road"
    assert first_vehicle.lane_label == "a"
    assert first_vehicle.position == pytest.approx(1.0)

    # ... AND the second vehicle continues
    assert second_vehicle.junction_label == "first_road"
    assert second_vehicle.lane_label == "b"
    assert second_vehicle.position == pytest.approx(2.5)

    # WHEN we keep going until the vehicles finish
    stepper.step(0.15)
    stepper.step(0.15)
    stepper.step(0.1)
    stepper.step(0.1)

    first_vehicle = vehicles.vehicle("first_vehicle")
    second_vehicle = vehicles.vehicle("second_vehicle")
    assert not is_active_vehicle(first_vehicle)
    assert not is_active_vehicle(second_vehicle)
