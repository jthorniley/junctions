import pytest
from junctions.network import LaneRef
from junctions.state.vehicles import (
    Vehicle,
    VehiclesState,
)


def test_insert_vehicle():
    # Given two vehicles on a lane
    vehicles = VehiclesState()
    vehicles.add_vehicle(Vehicle(LaneRef("road1", "a"), 0.0))
    vehicles.add_vehicle(Vehicle(LaneRef("road2", "b"), 0.0))

    label1, label2 = vehicles.vehicle_labels()

    # THEN I can retrieve the lane start state
    vehicle_state = vehicles.vehicle(label1)
    assert vehicle_state.lane_ref.junction == "road1"
    assert vehicle_state.lane_ref.lane == "a"
    assert vehicle_state.position == pytest.approx(0)

    vehicle_state = vehicles.vehicle(label2)
    assert vehicle_state.lane_ref.junction == "road2"
    assert vehicle_state.lane_ref.lane == "b"
    assert vehicle_state.position == pytest.approx(0)
