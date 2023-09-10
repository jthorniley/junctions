import pytest
from factory.random import randgen
from junctions.network import LaneRef
from junctions.state.vehicle_positions import VehiclePositions


def test_vehicle_positions():
    # Set up:
    # state object
    vehicle_positions = VehiclePositions()

    # two lane refs
    road_a = LaneRef(junction="road", lane="a")
    road_b = LaneRef(junction="road", lane="b")

    # act/assert - getting the lane refs is empty
    assert vehicle_positions[road_a] == ()
    assert vehicle_positions[road_b] == ()


def test_add_vehicle():
    # Set up:
    # state object
    vehicle_positions = VehiclePositions()
    road_a = LaneRef(junction="road", lane="a")
    road_b = LaneRef(junction="road", lane="b")

    # act put some new vehicles in lanes
    vehicle_positions.create_vehicle(road_a, 2.0)
    vehicle_positions.create_vehicle(road_a, 1.0)
    vehicle_positions.create_vehicle(road_a, 3.0)
    vehicle_positions.create_vehicle(road_b, 0.5)

    # ASSERT: can recall the positions, they come out sorted
    assert len(vehicle_positions[road_a])
    assert vehicle_positions[road_a][0] == pytest.approx(1.0)
    assert vehicle_positions[road_a][1] == pytest.approx(2.0)
    assert vehicle_positions[road_a][2] == pytest.approx(3.0)


@pytest.mark.parametrize("_fuzz", range(20))
def test_vehicle_position_sort(_fuzz):
    # Set up - generate random unsorted list
    values = [randgen.random() * 50 - 25 for _ in range(10)]

    # Act insert vehicles into state container
    vehicle_positions = VehiclePositions()

    for value in values:
        vehicle_positions.create_vehicle(LaneRef("a", "a"), value)

    # Assert - the list should be sorted when retrieved
    sorted_values = sorted(values)
    assert list(vehicle_positions[LaneRef("a", "a")]) == sorted_values
