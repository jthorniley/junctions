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
        height = (road.b.start[1] - road.a.end[1]) * 2.0
        width = road.a.end[0] - road.a.start[0]
        center_x = road.a.start[0] + width / 2.0
        center_y = road.a.start[1] + height / 2.0
        color = arcade.color.GRAY

        arcade.draw_rectangle_filled(center_x, center_y, width, height, color)


class JunctionsWindow(arcade.Window):
    scene: Scene = Scene()

    def __init__(self):
        screens = arcade.get_screens()
        super().__init__(800, 800, "Junctions", screen=screens[0])

        self.background_color = arcade.color.BUD_GREEN
        self.scene = Scene()

    def on_draw(self):
        self.clear()
        self.set_viewport(0, 200, 0, 200)
        self.scene.draw()

        super().on_draw()


def run():
    window = JunctionsWindow()

    example_road = create_road(np.array([5, 20]), road_length=80, lane_separation=10)
    window.scene.add_road(example_road)

    window.run()
