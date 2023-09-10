from junctions.network import LaneRef, Network
from junctions.state.vehicle_positions import VehiclePositions
from junctions.state.wait_flags import WaitFlags


def priority_wait(network: Network, vehicle_positions: VehiclePositions) -> WaitFlags:
    """Calculate wait flags across network"""
    wait_flags = WaitFlags()

    for current_lane_ref in network.all_lanes():
        junction = network.junction(current_lane_ref.junction)
        lane = junction.lanes[current_lane_ref.lane]
        lane_clear_time = lane.length / network.speed_limit(current_lane_ref)

        for priority_lane in junction.priority_over_lane(current_lane_ref.lane):
            priority_lane_ref = LaneRef(current_lane_ref.junction, priority_lane)

            if len(vehicle_positions.by_lane[priority_lane_ref]):
                wait_flags[current_lane_ref] = True
                break

            for feeder_lane_ref in network.feeder_lanes(priority_lane_ref):
                feeder_lane = network.lane(feeder_lane_ref)

                vehicles_on_feeder_lane = vehicle_positions.by_lane[feeder_lane_ref]

                if vehicles_on_feeder_lane.shape[0] > 0:
                    # Only the last vehicle position is relevant - if its not
                    # close enough to block the priority lane, then none of
                    # the vehicles behind are.
                    last_vehicle_position = vehicles_on_feeder_lane[-1]
                    feeder_lane_vehicle_time_left = (
                        feeder_lane.length - last_vehicle_position
                    ) / network.speed_limit(feeder_lane_ref)
                    if feeder_lane_vehicle_time_left < lane_clear_time:
                        wait_flags[current_lane_ref] = True
                        break

            if wait_flags[current_lane_ref]:
                # If any of the feeder lanes set the wait flag, we can break the outer
                # loop - don't need to check any more priority lanes
                break

    return wait_flags
