from tests.junctions.factories import ArcFactory, RoadFactory, TeeFactory

# test that the LANE_LABELS lists match up to the keys created
# by the lanes property - it always should


def test_road_lane_labels():
    road = RoadFactory.build()
    assert tuple(road.lanes.keys()) == road.LANE_LABELS


def test_arc_lane_labels():
    arc = ArcFactory.build()
    assert tuple(arc.lanes.keys()) == arc.LANE_LABELS


def test_tee_lane_labels():
    tee = TeeFactory.build()
    assert tuple(tee.lanes.keys()) == tee.LANE_LABELS
