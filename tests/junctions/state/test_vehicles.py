import pytest
from junctions.state.vehicles import (
    ActiveVehicle,
    InactiveVehicle,
    VehiclesState,
    is_active_vehicle,
)


def test_add_vehicle():
    # GIVEN vehicles state class
    vehicles = VehiclesState()

    # WHEN I add a vehicle
    new_state = vehicles.add_vehicle(InactiveVehicle())

    # THEN I get a generated label back
    label = "vehicle1"
    # ... and the original state is not changed
    assert tuple(vehicles.vehicle_labels()) == ()
    # ... and the label is in the list of vehicles
    assert tuple(new_state.vehicle_labels()) == (label,)
    # ... and we have an inactive vehicle in the set
    assert not new_state.vehicle(label).is_active


def test_insert_vehicle():
    # Given two vehicles on a lane
    vehicles = (
        VehiclesState()
        .add_vehicle(ActiveVehicle("road1", "a", 0.0))
        .add_vehicle(ActiveVehicle("road2", "b", 0.0))
    )
    label1, label2 = vehicles.vehicle_labels()

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


def test_update_vehicles():
    # Given a state object with an existing vehicle
    original_vehicle = ActiveVehicle("road1", "a", 0.0)
    new_vehicle_1 = ActiveVehicle("road2", "a", 1.0)
    new_vehicle_2 = ActiveVehicle("road3", "b", 2.0)

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
