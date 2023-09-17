import uuid

import numpy as np
import pytest
from factory.random import randgen
from junctions.network import LaneRef
from junctions.state.vehicle_positions import VehiclePositions
from numpy.testing import assert_almost_equal, assert_array_equal


def test_vehicle_positions():
    # Set up:
    # state object
    vehicle_positions = VehiclePositions()

    # two lane refs
    road_a = LaneRef(junction="road", lane="a")
    road_b = LaneRef(junction="road", lane="b")

    # act/assert - getting the lane refs is empty
    assert vehicle_positions.by_lane[road_a].shape == (0,)
    assert vehicle_positions.by_lane[road_b].shape == (0,)


def test_add_vehicle():
    # Set up:
    # state object
    vehicle_positions = VehiclePositions()
    road_a = LaneRef(junction="road", lane="a")
    road_b = LaneRef(junction="road", lane="b")

    # act put some new vehicles in lanes
    v1 = vehicle_positions.create_vehicle(road_a, 2.0)
    v2 = vehicle_positions.create_vehicle(road_a, 1.0)
    v3 = vehicle_positions.create_vehicle(road_a, 3.0)
    v4 = vehicle_positions.create_vehicle(road_b, 0.5)

    # ASSERT: can recall the positions, they come out sorted
    assert_almost_equal(vehicle_positions.by_lane[road_a], [1.0, 2.0, 3.0])
    assert_almost_equal(vehicle_positions.by_lane[road_b], [0.5])

    assert_array_equal(vehicle_positions.ids_by_lane[road_a], np.array([v2, v1, v3]))
    assert_array_equal(vehicle_positions.ids_by_lane[road_b], np.array([v4]))

    # Can also recall by ID
    assert vehicle_positions[v1] == {"lane_ref": road_a, "position": pytest.approx(2.0)}
    assert vehicle_positions[v2] == {"lane_ref": road_a, "position": pytest.approx(1.0)}
    assert vehicle_positions[v3] == {"lane_ref": road_a, "position": pytest.approx(3.0)}
    assert vehicle_positions[v4] == {"lane_ref": road_b, "position": pytest.approx(0.5)}


def test_invalid_lookup_id():
    vehicle_positions = VehiclePositions()
    with pytest.raises(KeyError):
        vehicle_positions[uuid.uuid4()]


@pytest.mark.parametrize("_fuzz", range(20))
def test_vehicle_position_sort(_fuzz):
    # Set up - generate random unsorted list
    values = [randgen.random() * 50 - 25 for _ in range(10)]

    # Act insert vehicles into state container
    vehicle_positions = VehiclePositions()

    for value in values:
        vehicle_positions.create_vehicle(LaneRef("a", "a"), value)

    # Assert - the list should be sorted when retrieved
    sorted_values = np.array(sorted(values), dtype=np.float32)
    assert_almost_equal(vehicle_positions.by_lane[LaneRef("a", "a")], sorted_values)


def test_move_to_new_lane():
    # SET UP: 10 vehicles on a single lane
    vehicle_positions = VehiclePositions()

    lane_1 = LaneRef("road1", "a")
    lane_2 = LaneRef("road2", "a")
    vehicles = [vehicle_positions.create_vehicle(lane_1, i) for i in range(10)]

    # ACT: move 3 vehicles to another lane
    vehicle_positions.switch_lane(vehicles[5], lane_2, position=2)
    vehicle_positions.switch_lane(vehicles[3], lane_2, position=0)
    vehicle_positions.switch_lane(vehicles[6], lane_2, position=3)

    # ASSERT:
    # non-switched vehicles have not changed...
    assert_almost_equal(
        vehicle_positions.by_lane[lane_1], [0.0, 1.0, 3.0, 6.0, 7.0, 8.0, 9.0]
    )
    assert_array_equal(
        vehicle_positions.ids_by_lane[lane_1],
        np.array(
            [
                vehicles[0],
                vehicles[1],
                vehicles[2],
                vehicles[4],
                vehicles[7],
                vehicles[8],
                vehicles[9],
            ]
        ),
    )

    # Switched vehicles are on new lane, in position order
    assert_almost_equal(vehicle_positions.by_lane[lane_2], [2.0, 4.0, 5.0])
    assert_array_equal(
        vehicle_positions.ids_by_lane[lane_2],
        np.array([vehicles[3], vehicles[5], vehicles[6]]),
    )
