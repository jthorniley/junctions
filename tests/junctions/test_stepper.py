import pytest
from junctions.network import Network
from junctions.stepper import Stepper
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
