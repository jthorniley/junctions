import random
from shutil import move

from junctions.network import Network
from junctions.state.vehicles import (
    ActiveVehicle,
    InactiveVehicle,
    Vehicle,
    VehiclesState,
    is_active_vehicle,
)


class Stepper:
    """Utility for stepping the simulation in time"""

    def __init__(self, network: Network):
        self._network = network

    def _calculate_vehicle_update(self, dt: float, vehicle: ActiveVehicle) -> Vehicle:
        speed = self._network.speed_limit(vehicle.junction_label, vehicle.lane_label)
        movement = speed * dt

        next_position = vehicle.position + movement

        lane = self._network.lane(vehicle.junction_label, vehicle.lane_label)

        if (excess := next_position - lane.length) > 0:
            t_excess = excess / speed

            next_lane_choices = self._network.connected_lanes(
                vehicle.junction_label, vehicle.lane_label
            )

            if next_lane_choices:
                next_lane_label = random.choice(next_lane_choices)

                next_lane_speed_limit = self._network.speed_limit(*next_lane_label)

                return ActiveVehicle(
                    junction_label=next_lane_label[0],
                    lane_label=next_lane_label[1],
                    position=t_excess * next_lane_speed_limit,
                )

            else:
                return InactiveVehicle()
        else:
            return ActiveVehicle(
                junction_label=vehicle.junction_label,
                lane_label=vehicle.lane_label,
                position=next_position,
            )

    def step(self, dt: float, vehicles_state: VehiclesState) -> VehiclesState:
        """Perform a step with time interval dt"""

        updates = {}

        for vehicle_label, vehicle in vehicles_state.items():
            if is_active_vehicle(vehicle):
                updates[vehicle_label] = self._calculate_vehicle_update(dt, vehicle)

        return vehicles_state.with_updates(updates)
