import math
import random
from time import time

from junctions.network import Network
from junctions.state.vehicles import ActiveVehicle, VehiclesState
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
    road2 = Road(
        (*tee.branch_a.lanes["a"].end,),
        bearing=math.pi,
        road_length=50,
        lane_separation=6,
    )
    network.add_junction(road)
    network.add_junction(tee)
    network.add_junction(road1)
    network.add_junction(road2)
    network.connect_lanes("road1", "a", "tee1", "a")
    network.connect_lanes("road1", "a", "tee1", "c")
    network.connect_lanes("road2", "b", "tee1", "b")
    network.connect_lanes("road2", "b", "tee1", "f")
    network.connect_lanes("road3", "b", "tee1", "d")
    network.connect_lanes("road3", "b", "tee1", "e")
    network.connect_lanes("tee1", "a", "road2", "a")
    network.connect_lanes("tee1", "b", "road1", "b")
    network.connect_lanes("tee1", "c", "road3", "a")
    network.connect_lanes("tee1", "d", "road1", "b")
    network.connect_lanes("tee1", "e", "road2", "a")
    network.connect_lanes("tee1", "f", "road3", "a")

    network_renderer = NetworkRenderer(network)
    stepper = Stepper(network)

    # Double the scale
    win.view = Mat4.from_scale(Vec3(2, 2, 1))

    t = time()
    vehicles_state = (
        VehiclesState()
        .add_vehicle(
            ActiveVehicle(junction_label="road1", lane_label="a", position=10.0)
        )
        .add_vehicle(
            ActiveVehicle(junction_label="road2", lane_label="b", position=10.0)
        )
        .add_vehicle(
            ActiveVehicle(junction_label="road3", lane_label="b", position=10.0)
        )
    )

    @win.event
    def on_draw():
        nonlocal vehicles_state, t
        win.clear()
        network_renderer.draw()

        dt = time() - t
        t += dt

        if random.random() < dt:
            # Add approximately 1 vehicle/second
            choices = (("road1", "a"), ("road2", "b"), ("road3", "b"))
            where = random.choice(choices)
            vehicles_state = vehicles_state.add_vehicle(
                ActiveVehicle(where[0], where[1], 0.0)
            )

        vehicles_state = stepper.step(dt, vehicles_state)

        vehicles_state_renderer = VehiclesStateRenderer(network, vehicles_state)
        vehicles_state_renderer.draw()

    app.run()
