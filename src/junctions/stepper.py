import random

from junctions.network import Network
from junctions.vehicles import Vehicles, is_active_vehicle


class Stepper:
    """Utility for stepping the simulation in time"""

    def __init__(self, network: Network, vehicles: Vehicles):
        self._network = network
        self._vehicles = vehicles

    def step(self, dt: float):
        """Perform a step with time interval dt"""

        for vehicle_label, vehicle in self._vehicles.items():
            if is_active_vehicle(vehicle):
                speed = self._network.speed_limit(
                    vehicle.junction_label, vehicle.lane_label
                )
                movement = speed * dt
                vehicle.position += movement

                lane = self._network.lane(vehicle.junction_label, vehicle.lane_label)

                if (excess := vehicle.position - lane.length) > 0:
                    t_excess = excess / speed

                    next_lane_choices = self._network.connected_lanes(
                        vehicle.junction_label, vehicle.lane_label
                    )

                    if next_lane_choices:
                        next_lane_label = random.choice(next_lane_choices)

                        vehicle.junction_label = next_lane_label[0]
                        vehicle.lane_label = next_lane_label[1]
                        next_lane_speed_limit = self._network.speed_limit(
                            *next_lane_label
                        )

                        vehicle.position = t_excess * next_lane_speed_limit
                    else:
                        self._vehicles.deactivate(vehicle_label)
