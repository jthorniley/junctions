import numpy as np
from junctions.primitives import create_road
from numpy.testing import assert_allclose


def test_create_road():
    road = create_road(np.array([0.2, 0]), 10, 4)

    assert_allclose(road.a.start, np.array([0.2, 0]))
    assert_allclose(road.a.end, np.array([0.2, 10]))
    assert_allclose(road.b.start, np.array([4.2, 10]))
    assert_allclose(road.b.end, np.array([4.2, 0]))
