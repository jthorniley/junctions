from junctions.network import LaneRef


class WaitFlags:
    def __init__(self):
        self._wait_flags: set[LaneRef] = set()

    def __getitem__(self, lane_ref: LaneRef) -> bool:
        return lane_ref in self._wait_flags

    def __setitem__(self, lane_ref: LaneRef, value: bool) -> None:
        if value:
            self._wait_flags |= {lane_ref}
        else:
            try:
                self._wait_flags.remove(lane_ref)
            except KeyError:
                # Not an existing member of the set - does not matter
                pass
