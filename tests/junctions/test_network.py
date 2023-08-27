import pytest
from junctions.network import Network

from tests.junctions.factories import ArcFactory, RoadFactory


def test_add_road_to_network():
    # WHEN I have a network
    network = Network()

    # AND I add a road to the network
    road = RoadFactory.build()
    network.add_junction(road)

    # THEN the road is in the network junction list
    assert list(network.all_junctions()) == [road]


def test_add_road_default_label():
    # WHEN I have a network
    network = Network()

    # AND I add a road to the network
    road = RoadFactory.build()
    label = network.add_junction(road)

    # THEN the road is labelled road1
    assert label == "road1"
    assert network.junction_lookup == {"road1": road}


def test_add_arc_default_label():
    # WHEN I have a network
    network = Network()

    # AND I add a arc to the network
    arc = ArcFactory.build()
    label = network.add_junction(arc)

    # THEN the arc is labelled arc1
    assert label == "arc1"
    assert network.junction_lookup == {"arc1": arc}


def test_add_arcs_and_roads_default_labels():
    # WHEN I have a network
    network = Network()

    # And I add two arcs and three roads to the network
    arcs = ArcFactory.build_batch(2)
    roads = RoadFactory.build_batch(3)

    network.add_junction(arcs[0])
    network.add_junction(roads[0])
    network.add_junction(arcs[1])
    network.add_junction(roads[1])
    network.add_junction(roads[2])

    # Then the arcs and roads get incrementing default labels
    assert network.junction_lookup == {
        "arc1": arcs[0],
        "arc2": arcs[1],
        "road1": roads[0],
        "road2": roads[1],
        "road3": roads[2],
    }


def test_add_arcs_and_roads_custom_labels():
    # WHEN I have a network
    network = Network()

    # AND I add two arcs and three roads, with custom labels for some
    arcs = ArcFactory.build_batch(2)
    roads = RoadFactory.build_batch(3)

    network.add_junction(arcs[0])
    first_road_label = network.add_junction(roads[0], "first_road")
    second_arc_label = network.add_junction(arcs[1], "second_arc")
    network.add_junction(roads[1])
    network.add_junction(roads[2])

    # THEN the custom labels are used where appropriate
    assert first_road_label == "first_road"
    assert second_arc_label == "second_arc"
    assert network.junction_lookup == {
        "arc1": arcs[0],
        "second_arc": arcs[1],
        "first_road": roads[0],
        "road1": roads[1],
        "road2": roads[2],
    }


def test_cannot_add_same_label_twice():
    # WHEN I have a network
    network = Network()

    # AND I have added the first junction
    arc1 = ArcFactory.build()
    network.add_junction(arc1, label="foo")

    # THEN an exception is raised if I add another junction with the same label
    arc2 = ArcFactory.build()
    with pytest.raises(ValueError):
        network.add_junction(arc2, label="foo")

    # AND only the first junction is added to the network
    assert network.junction_lookup == {"foo": arc1}


def test_junction_lookup_is_immutable():
    # GIVEN a network with a junction
    network = Network()
    arc1 = ArcFactory.build()
    network.add_junction(arc1, label="foo")
    assert network.junction_lookup == {"foo": arc1}

    # WHEN I try to modify the lookup directly
    # THEN it is an error
    with pytest.raises(TypeError):
        network.junction_lookup["foo"] = "bar"  # type: ignore

    # AND the network is unchanged
    assert network.junction_lookup == {"foo": arc1}


def test_get_lane_labels_road():
    # GIVEN a network with a road
    network = Network()
    road1 = RoadFactory.build()
    network.add_junction(road1, "road1")

    # WHEN I request all labels
    labels = network.lane_labels("road1")

    # THEN the result is the lane labels for the road
    assert labels == ("a", "b")


def test_connectivity():
    # GIVEN a network
    network = Network()

    # ... with 3 roads
    roads = RoadFactory.build_batch(3)
    for road in roads:
        network.add_junction(road)

    # WHEN I connect the roads together
    network.connect_lanes("road1", "a", "road2", "a")
    network.connect_lanes("road1", "a", "road3", "a")
    network.connect_lanes("road1", "b", "road2", "b")
    network.connect_lanes("road1", "b", "road3", "b")

    # THEN I can query the connectivity
    assert network.connected_lanes("road1", "a") == (("road2", "a"), ("road3", "a"))
    assert network.connected_lanes("road1", "b") == (("road2", "b"), ("road3", "b"))
    # ... road2-a is not connected to anything
    assert network.connected_lanes("road2", "a") == ()
    # ... blah-foo does not exist
    assert network.connected_lanes("blah", "foo") == ()
