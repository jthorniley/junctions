import math
import random

import pytest
from factory import Factory, LazyFunction
from junctions.network import Network
from junctions.types import Arc, Road


class RoadFactory(Factory):
    class Meta:
        model = Road

    origin = LazyFunction(lambda: (random.random() * 100, random.random() * 100))
    bearing = LazyFunction(lambda: (random.random() * 2 * math.pi))
    road_length = LazyFunction(lambda: (random.random() * 100))
    lane_separation = LazyFunction(lambda: (random.random() * 10))


class ArcFactory(Factory):
    class Meta:
        model = Arc

    origin = LazyFunction(lambda: (random.random() * 100, random.random() * 100))
    bearing = LazyFunction(lambda: (random.random() * math.pi))
    arc_length = LazyFunction(lambda: (random.random() * math.pi))
    arc_radius = LazyFunction(lambda: (random.random() * 20))
    lane_separation = LazyFunction(lambda: (random.random() * 10))


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
    network.add_junction(road)

    # THEN the road is labelled road1
    assert network.junction_lookup == {"road1": road}


def test_add_arc_default_label():
    # WHEN I have a network
    network = Network()

    # AND I add a arc to the network
    arc = ArcFactory.build()
    network.add_junction(arc)

    # THEN the arc is labelled arc1
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
    network.add_junction(roads[0], "first_road")
    network.add_junction(arcs[1], "second_arc")
    network.add_junction(roads[1])
    network.add_junction(roads[2])

    # THEN the custom labels are used where appropriate
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
