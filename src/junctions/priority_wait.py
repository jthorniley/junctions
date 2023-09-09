from collections import defaultdict

from junctions.network import LaneRef, Network
from junctions.state.vehicles import VehiclesState
from junctions.state.wait_flags import WaitFlags


def priority_wait(network: Network, vehicles_state: VehiclesState) -> WaitFlags:
    """Calculate wait flags across network"""
    wait_flags = WaitFlags()

    lane_vehicle_map = defaultdict(list)
    for _, vehicle in vehicles_state.items():
        lane_vehicle_map[vehicle.lane_ref].append(vehicle)

    for junction_label in network.junction_labels():
        junction = network.junction(junction_label)

        for lane_label in junction.LANE_LABELS:
            for priority_lane in junction.priority_over_lane(lane_label):
                if len(lane_vehicle_map[LaneRef(junction_label, priority_lane)]):
                    wait_flags[LaneRef(junction_label, lane_label)] = True
                    break

    return wait_flags
