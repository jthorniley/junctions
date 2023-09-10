from collections import defaultdict

from junctions.network import LaneRef, Network
from junctions.state.vehicles import _Vehicle, _VehiclesState
from junctions.state.wait_flags import WaitFlags


def priority_wait(network: Network, vehicles_state: _VehiclesState) -> WaitFlags:
    """Calculate wait flags across network"""
    wait_flags = WaitFlags()

    lane_vehicle_map: defaultdict[LaneRef, list[_Vehicle]] = defaultdict(list)
    for _, vehicle in vehicles_state.items():
        lane_vehicle_map[vehicle.lane_ref].append(vehicle)

    for junction_label, junction in network.all_junctions():
        for lane_label, lane in junction.lanes.items():
            current_lane_ref = LaneRef(junction_label, lane_label)

            lane_clear_time = lane.length / network.speed_limit(current_lane_ref)

            for priority_lane in junction.priority_over_lane(lane_label):
                priority_lane_ref = LaneRef(junction_label, priority_lane)
                if len(lane_vehicle_map[priority_lane_ref]):
                    wait_flags[current_lane_ref] = True
                    break

                for feeder_lane_ref in network.feeder_lanes(priority_lane_ref):
                    feeder_lane = network.lane(feeder_lane_ref)
                    for feeder_lane_vehicle in lane_vehicle_map[feeder_lane_ref]:
                        feeder_lane_vehicle_time_left = (
                            feeder_lane.length - feeder_lane_vehicle.position
                        ) / network.speed_limit(feeder_lane_ref)
                        if feeder_lane_vehicle_time_left < lane_clear_time:
                            wait_flags[current_lane_ref] = True
                            break

    return wait_flags
