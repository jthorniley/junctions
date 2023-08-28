import pytest
from junctions.vehicles import Vehicles, is_active_vehicle


def test_add_vehicle():
    # GIVEN vehicles state class
    vehicles = Vehicles()

    # WHEN I add a vehicle
    label = vehicles.add_vehicle()

    # THEN I get a generated label back
    assert label == "vehicle1"
    # ... and the label is in the list of vehicles
    assert vehicles.vehicle_labels() == (label,)
    # ... and we have an inactive vehicle in the set
    assert not vehicles.vehicle(label).is_active


def test_insert_vehicle():
    # Given two vehicles
    vehicles = Vehicles()
    label1 = vehicles.add_vehicle()
    label2 = vehicles.add_vehicle()

    # WHEN I activate them on a lane
    vehicles.move_to_lane_start(label1, "road1", "a")
    vehicles.move_to_lane_start(label2, "road2", "b")

    # THEN I can retrieve the lane start state
    vehicle_state = vehicles.vehicle(label1)
    assert is_active_vehicle(vehicle_state)
    assert vehicle_state.junction_label == "road1"
    assert vehicle_state.lane_label == "a"
    assert vehicle_state.position == pytest.approx(0)

    vehicle_state = vehicles.vehicle(label2)
    assert is_active_vehicle(vehicle_state)
    assert vehicle_state.junction_label == "road2"
    assert vehicle_state.lane_label == "b"
    assert vehicle_state.position == pytest.approx(0)
