from junctions.network import LaneRef
from junctions.state.wait_flags import WaitFlags


def test_wait_flags_default_off():
    wait_flags = WaitFlags()

    assert not wait_flags[LaneRef("a", "b")]
    assert not wait_flags[LaneRef("c", "d")]


def test_wait_flags_stays_off():
    wait_flags = WaitFlags()

    wait_flags[LaneRef("a", "b")] = False

    assert not wait_flags[LaneRef("a", "b")]
    assert not wait_flags[LaneRef("c", "d")]


def test_set_wait_flag():
    wait_flags = WaitFlags()

    wait_flags[LaneRef("a", "b")] = True

    assert wait_flags[LaneRef("a", "b")]
    assert not wait_flags[LaneRef("c", "d")]

    wait_flags[LaneRef("a", "b")] = False

    assert not wait_flags[LaneRef("a", "b")]
    assert not wait_flags[LaneRef("c", "d")]

    wait_flags[LaneRef("a", "b")] = True

    assert wait_flags[LaneRef("a", "b")]
    assert not wait_flags[LaneRef("c", "d")]
