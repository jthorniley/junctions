import math
import random
from time import time

from junctions.network import LaneRef, Network
from junctions.state.vehicles import Vehicle, VehiclesState
from junctions.stepper import Stepper
from junctions.types import Road, Tee
from pyglet import app, window
from pyglet.math import Mat4, Vec3

from viewer.network_renderer import NetworkRenderer
from viewer.vehicles_state_renderer import VehiclesStateRenderer


def run():
    win = window.Window(width=500, height=500)

    network = Network()

    road = Road((20, 100), bearing=math.pi / 2, road_length=100, lane_separation=6)
    tee = Tee(
        (120, 100),
        main_road_bearing=math.pi / 2,
        main_road_length=20,
        lane_separation=6,
    )
    road1 = Road((140, 100), bearing=math.pi / 2, road_length=80, lane_separation=6)
    road_2_start = tee.branch_a.lanes["a"].end
    road2 = Road(
        (road_2_start.x, road_2_start.y),
        bearing=math.pi,
        road_length=50,
        lane_separation=6,
    )
    network.add_junction(road)
    network.add_junction(tee)
    network.add_junction(road1)
    network.add_junction(road2)
    network.connect_lanes(LaneRef("road1", "a"), LaneRef("tee1", "a"))
    network.connect_lanes(LaneRef("road1", "a"), LaneRef("tee1", "c"))
    network.connect_lanes(LaneRef("road2", "b"), LaneRef("tee1", "b"))
    network.connect_lanes(LaneRef("road2", "b"), LaneRef("tee1", "f"))
    network.connect_lanes(LaneRef("road3", "b"), LaneRef("tee1", "d"))
    network.connect_lanes(LaneRef("road3", "b"), LaneRef("tee1", "e"))
    network.connect_lanes(LaneRef("tee1", "a"), LaneRef("road2", "a"))
    network.connect_lanes(LaneRef("tee1", "b"), LaneRef("road1", "b"))
    network.connect_lanes(LaneRef("tee1", "c"), LaneRef("road3", "a"))
    network.connect_lanes(LaneRef("tee1", "d"), LaneRef("road1", "b"))
    network.connect_lanes(LaneRef("tee1", "e"), LaneRef("road2", "a"))
    network.connect_lanes(LaneRef("tee1", "f"), LaneRef("road3", "a"))

    stepper = Stepper(network)

    # Double the scale
    win.view = Mat4.from_scale(Vec3(2, 2, 1))

    t = time()
    vehicles_state = VehiclesState()
    last_new_vehicle_time = t

    @win.event
    def on_draw():
        nonlocal vehicles_state, t, last_new_vehicle_time
        win.clear()

        dt = time() - t
        t += dt

        if random.random() / 2 < dt and last_new_vehicle_time < (t - 0.5):
            choices = (
                LaneRef("road1", "a"),
                LaneRef("road2", "b"),
                LaneRef("road3", "b"),
            )
            where = random.choice(choices)
            vehicles_state.add_vehicle(Vehicle(where, 0.0))
            last_new_vehicle_time = t

        vehicles_state = stepper.step(dt, vehicles_state)

        network_renderer = NetworkRenderer(network, stepper.wait_flags)
        vehicles_state_renderer = VehiclesStateRenderer(network, vehicles_state)
        network_renderer.draw()
        vehicles_state_renderer.draw()

    app.run()
