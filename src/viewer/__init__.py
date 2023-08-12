import arcade
import arcade.color
import numpy as np
from junctions.primitives import create_road
from junctions.types import Road


class Scene:
    roads: list[Road]

    def __init__(self):
        self.roads = []

    def add_road(self, road: Road):
        self.roads.append(road)

    def draw(self):
        self.draw_roads()

    def draw_roads(self):
        for road in self.roads:
            Scene.draw_road(road)

    @staticmethod
    def draw_road(road: Road):
        shape = Scene.create_road_shape(road)
        shape.draw()

    @staticmethod
    def create_road_shape(road: Road) -> arcade.Shape:
        a_vec = road.a.end - road.a.start
        perp_vec = road.b.end - road.a.start

        x0 = road.a.start - perp_vec / 2
        x1 = x0 + a_vec
        x2 = x1 + perp_vec * 2
        x3 = x2 - a_vec

        return arcade.create_rectangle_filled_with_colors(
            [x0, x1, x2, x3], [arcade.color.BLUE] * 4
        )


class JunctionsWindow(arcade.Window):
    scene: Scene = Scene()

    def __init__(self):
        screens = arcade.get_screens()
        super().__init__(400, 400, "Junctions", screen=screens[0])

        self.background_color = arcade.color.BUD_GREEN
        self.scene = Scene()

    def on_draw(self):
        self.clear()
        self.set_viewport(0, 200, 0, 200)
        self.scene.draw()

        super().on_draw()


def run():
    window = JunctionsWindow()

    example_road = create_road(np.array([5, 10]), road_length=80, lane_separation=10)
    print(example_road)
    window.scene.add_road(example_road)

    window.run()
