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
    assert vehicle_positions.positions_by_lane[road_a].shape == (0,)
    assert vehicle_positions.positions_by_lane[road_b].shape == (0,)


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
    v5 = vehicle_positions.create_vehicle(road_a, 2.1)

    # ASSERT: can recall the positions, they come out sorted
    assert_almost_equal(
        vehicle_positions.positions_by_lane[road_a], [1.0, 2.0, 2.1, 3.0]
    )
    assert_almost_equal(vehicle_positions.positions_by_lane[road_b], [0.5])

    assert_array_equal(
        vehicle_positions.ids_by_lane[road_a], np.array([v2, v1, v5, v3])
    )
    assert_array_equal(vehicle_positions.ids_by_lane[road_b], np.array([v4]))

    # Can also recall by ID
    assert vehicle_positions[v1] == {"lane_ref": road_a, "position": pytest.approx(2.0)}
    assert vehicle_positions[v2] == {"lane_ref": road_a, "position": pytest.approx(1.0)}
    assert vehicle_positions[v3] == {"lane_ref": road_a, "position": pytest.approx(3.0)}
    assert vehicle_positions[v4] == {"lane_ref": road_b, "position": pytest.approx(0.5)}
    assert vehicle_positions[v5] == {"lane_ref": road_a, "position": pytest.approx(2.1)}


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
    assert_almost_equal(
        vehicle_positions.positions_by_lane[LaneRef("a", "a")], sorted_values
    )


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
        vehicle_positions.positions_by_lane[lane_1], [0.0, 1.0, 2.0, 4.0, 7.0, 8.0, 9.0]
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
    # old vehicle lookups are correct
    assert vehicle_positions[vehicles[0]] == {
        "lane_ref": lane_1,
        "position": pytest.approx(0.0),
    }
    assert vehicle_positions[vehicles[1]] == {
        "lane_ref": lane_1,
        "position": pytest.approx(1.0),
    }
    assert vehicle_positions[vehicles[2]] == {
        "lane_ref": lane_1,
        "position": pytest.approx(2.0),
    }
    assert vehicle_positions[vehicles[4]] == {
        "lane_ref": lane_1,
        "position": pytest.approx(4.0),
    }
    assert vehicle_positions[vehicles[7]] == {
        "lane_ref": lane_1,
        "position": pytest.approx(7.0),
    }
    assert vehicle_positions[vehicles[8]] == {
        "lane_ref": lane_1,
        "position": pytest.approx(8.0),
    }
    assert vehicle_positions[vehicles[9]] == {
        "lane_ref": lane_1,
        "position": pytest.approx(9.0),
    }

    # Switched vehicles are on new lane, in position order
    assert_almost_equal(vehicle_positions.positions_by_lane[lane_2], [0.0, 2.0, 3.0])
    assert_array_equal(
        vehicle_positions.ids_by_lane[lane_2],
        np.array([vehicles[3], vehicles[5], vehicles[6]]),
    )
    assert vehicle_positions[vehicles[5]] == {
        "lane_ref": lane_2,
        "position": pytest.approx(2.0),
    }
    assert vehicle_positions[vehicles[3]] == {
        "lane_ref": lane_2,
        "position": pytest.approx(0.0),
    }
    assert vehicle_positions[vehicles[6]] == {
        "lane_ref": lane_2,
        "position": pytest.approx(3.0),
    }


def test_clone():
    # SET UP: vehicle positions with a vehicle
    vehicle_positions = VehiclePositions()
    v = vehicle_positions.create_vehicle(LaneRef("road1", "a"), 1.0)

    # ACT: clone the object, and move on the clone
    clone_vehicle_positions = vehicle_positions.copy()
    clone_vehicle_positions.positions_by_lane[LaneRef("road1", "a")][0] += 1

    # ASSERT: the clone reflects the move, the original doesnt
    assert_almost_equal(
        clone_vehicle_positions.positions_by_lane[LaneRef("road1", "a")], [2.0]
    )
    assert_almost_equal(
        vehicle_positions.positions_by_lane[LaneRef("road1", "a")], [1.0]
    )
    assert_array_equal(
        clone_vehicle_positions.ids_by_lane[LaneRef("road1", "a")], np.array([v])
    )
    assert_array_equal(
        vehicle_positions.ids_by_lane[LaneRef("road1", "a")], np.array([v])
    )
    assert vehicle_positions[v] == {"lane_ref": LaneRef("road1", "a"), "position": 1.0}
    assert clone_vehicle_positions[v] == {
        "lane_ref": LaneRef("road1", "a"),
        "position": 2.0,
    }


def test_remove_vehicle():
    # SET UP: create some vehicles
    vehicle_positions = VehiclePositions()
    a = vehicle_positions.create_vehicle(LaneRef("road1", "a"), 1.0)
    b = vehicle_positions.create_vehicle(LaneRef("road1", "a"), 2.0)
    c = vehicle_positions.create_vehicle(LaneRef("road1", "a"), 3.0)
    d = vehicle_positions.create_vehicle(LaneRef("road1", "a"), 4.0)

    # ACT: remove from middle
    vehicle_positions.remove(b)

    # ASSERT vehicle is gone:
    with pytest.raises(KeyError):
        vehicle_positions[b]

    assert_array_equal(
        vehicle_positions.ids_by_lane[LaneRef("road1", "a")], np.array([a, c, d])
    )

    # other vehicle are still correct
    assert vehicle_positions[c] == {
        "lane_ref": LaneRef("road1", "a"),
        "position": pytest.approx(3.0),
    }
    # other vehicle are still correct
    assert vehicle_positions[d] == {
        "lane_ref": LaneRef("road1", "a"),
        "position": pytest.approx(4.0),
    }


def test_remove_vehicle_from_end():
    # SET UP: create some vehicles
    vehicle_positions = VehiclePositions()
    a = vehicle_positions.create_vehicle(LaneRef("road1", "a"), 1.0)
    b = vehicle_positions.create_vehicle(LaneRef("road1", "a"), 2.0)
    c = vehicle_positions.create_vehicle(LaneRef("road1", "a"), 3.0)
    d = vehicle_positions.create_vehicle(LaneRef("road1", "a"), 4.0)

    # ACT: remove from end
    vehicle_positions.remove(d)

    # ASSERT vehicle is gone:
    with pytest.raises(KeyError):
        vehicle_positions[d]

    assert_array_equal(
        vehicle_positions.ids_by_lane[LaneRef("road1", "a")], np.array([a, b, c])
    )

    # other vehicle are still correct
    assert vehicle_positions[c] == {
        "lane_ref": LaneRef("road1", "a"),
        "position": pytest.approx(3.0),
    }
    # other vehicle are still correct
    assert vehicle_positions[b] == {
        "lane_ref": LaneRef("road1", "a"),
        "position": pytest.approx(2.0),
    }


def test_remove_vehicle_from_start():
    # SET UP: create some vehicles
    vehicle_positions = VehiclePositions()
    a = vehicle_positions.create_vehicle(LaneRef("road1", "a"), 1.0)
    b = vehicle_positions.create_vehicle(LaneRef("road1", "a"), 2.0)
    c = vehicle_positions.create_vehicle(LaneRef("road1", "a"), 3.0)
    d = vehicle_positions.create_vehicle(LaneRef("road1", "a"), 4.0)

    # ACT: remove from start
    vehicle_positions.remove(a)

    # ASSERT vehicle is gone:
    with pytest.raises(KeyError):
        vehicle_positions[a]

    assert_array_equal(
        vehicle_positions.ids_by_lane[LaneRef("road1", "a")], np.array([b, c, d])
    )

    # other vehicle are still correct
    assert vehicle_positions[c] == {
        "lane_ref": LaneRef("road1", "a"),
        "position": pytest.approx(3.0),
    }
    # other vehicle are still correct
    assert vehicle_positions[d] == {
        "lane_ref": LaneRef("road1", "a"),
        "position": pytest.approx(4.0),
    }


def test_iterate_all_vehicles():
    # SET UP: some vehicles on multiple lanes
    vehicle_positions = VehiclePositions()
    v1 = vehicle_positions.create_vehicle(LaneRef("road1", "a"), 0.0)
    v2 = vehicle_positions.create_vehicle(LaneRef("road1", "a"), 1.0)
    v3 = vehicle_positions.create_vehicle(LaneRef("road2", "a"), 2.0)
    v4 = vehicle_positions.create_vehicle(LaneRef("road2", "a"), 3.0)

    # ACT: iterate
    all_lanes = []
    all_vehicles = []
    for lane, vehicles in vehicle_positions.group_by_lane():
        all_lanes.append(lane)
        all_vehicles.append(vehicles)

    # ASSERT: all the expected vehicles are in the set
    assert all_lanes == [LaneRef("road1", "a"), LaneRef("road2", "a")]
    assert_array_equal(all_vehicles[0]["id"], np.array([v1, v2]))
    assert_array_equal(all_vehicles[1]["id"], np.array([v3, v4]))
    assert_almost_equal(all_vehicles[0]["position"], np.array([0.0, 1.0]))
    assert_almost_equal(all_vehicles[1]["position"], np.array([2.0, 3.0]))
