from junctions.network import Network
from junctions.vehicles import Vehicles, is_active_vehicle


class Stepper:
    """Utility for stepping the simulation in time"""

    def __init__(self, network: Network, vehicles: Vehicles):
        self._network = network
        self._vehicles = vehicles

    def step(self, dt: float):
        """Perform a step with time interval dt"""

        for _, vehicle in self._vehicles.items():
            if is_active_vehicle(vehicle):
                speed = self._network.speed_limit(
                    vehicle.junction_label, vehicle.lane_label
                )
                movement = speed * dt
                vehicle.position += movement
