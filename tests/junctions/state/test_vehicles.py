import pytest
from junctions.state.vehicles import (
    Vehicle,
    VehiclesState,
)


def test_insert_vehicle():
    # Given two vehicles on a lane
    vehicles = (
        VehiclesState()
        .add_vehicle(Vehicle("road1", "a", 0.0))
        .add_vehicle(Vehicle("road2", "b", 0.0))
    )
    label1, label2 = vehicles.vehicle_labels()

    # THEN I can retrieve the lane start state
    vehicle_state = vehicles.vehicle(label1)
    assert vehicle_state.junction_label == "road1"
    assert vehicle_state.lane_label == "a"
    assert vehicle_state.position == pytest.approx(0)

    vehicle_state = vehicles.vehicle(label2)
    assert vehicle_state.junction_label == "road2"
    assert vehicle_state.lane_label == "b"
    assert vehicle_state.position == pytest.approx(0)


def test_update_vehicles():
    # Given a state object with an existing vehicle
    original_vehicle = Vehicle("road1", "a", 0.0)
    new_vehicle_1 = Vehicle("road2", "a", 1.0)
    new_vehicle_2 = Vehicle("road3", "b", 2.0)

    vehicles = VehiclesState().add_vehicle(original_vehicle)
    (label1,) = vehicles.vehicle_labels()

    # WHEN I call with_updates with changes to the existing vehicle and a new vehicle
    new_vehicles = vehicles.with_updates(
        {
            label1: new_vehicle_1,
            "new_vehicle": new_vehicle_2,
        }
    )

    # THEN the state is updated with the new vehicles
    assert list(vehicles.items()) == [(label1, original_vehicle)]
    assert list(new_vehicles.items()) == [
        (label1, new_vehicle_1),
        ("new_vehicle", new_vehicle_2),
    ]

    # WHEN I call with None
    new_vehicles = new_vehicles.with_updates({label1: None})

    # THEN that vehicle is removed
    assert list(new_vehicles.items()) == [
        ("new_vehicle", new_vehicle_2),
    ]
