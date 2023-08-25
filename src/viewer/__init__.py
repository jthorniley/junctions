import math

from junctions.network import Network
from junctions.types import Road, Tee
from pyglet import app, window
from pyglet.math import Mat4, Vec3

from viewer.network_renderer import NetworkRenderer


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
        (*tee.branch_a.lanes[0].end,),
        bearing=math.pi,
        road_length=50,
        lane_separation=6,
    )
    network.add_junction(road)
    network.add_junction(tee)
    network.add_junction(road1)
    network.add_junction(road2)

    network_renderer = NetworkRenderer(network.junction_lookup)

    # Double the scale
    win.view = Mat4.from_scale(Vec3(2, 2, 1))

    @win.event
    def on_draw():
        win.clear()
        network_renderer.draw()

    app.run()
