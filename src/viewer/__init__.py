import math

from junctions.network import Network
from junctions.types import Arc, Road
from pyglet import app, window
from pyglet.math import Mat4, Vec3

from viewer.network_renderer import NetworkRenderer


def run():
    win = window.Window(width=500, height=500)
    network = Network()
    network_renderer = NetworkRenderer(network)

    @win.event
    def on_draw():
        win.clear()
        network_renderer.draw()

    # Double the scale
    win.view = Mat4.from_scale(Vec3(2, 2, 1))

    road_a = Road((20, 50), bearing=math.pi / 2, road_length=40, lane_separation=8)
    road_b = Road((60, 50), bearing=math.pi / 2, road_length=28, lane_separation=8)
    road_c = Road((88, 50), bearing=math.pi / 2, road_length=40, lane_separation=8)

    curve_a = Arc(
        (70, 68),
        bearing=math.pi,
        arc_radius=10,
        arc_length=math.pi / 2,
        lane_separation=8,
    )
    curve_b = Arc(
        (88, 58),
        bearing=3 * math.pi / 2,
        arc_radius=10,
        arc_length=math.pi / 2,
        lane_separation=8,
    )

    road_d = Road(
        (curve_a.lanes[1].end.x, curve_a.lanes[1].end.y),
        bearing=0,
        road_length=50,
        lane_separation=8,
    )
    network.add_junction(road_a)
    network.add_junction(road_b)
    network.add_junction(road_c)
    network.add_junction(curve_a)
    network.add_junction(curve_b)
    network.add_junction(road_d)
    app.run()
