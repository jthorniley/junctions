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
    def create_road_shape(road: Road) -> arcade.ShapeElementList:
        a_vec = road.a.end - road.a.start
        perp_vec = road.b.end - road.a.start

        x0 = road.a.start - perp_vec / 2
        x1 = x0 + a_vec
        x2 = x1 + perp_vec * 2
        x3 = x2 - a_vec

        shape_list = arcade.ShapeElementList()

        base = arcade.create_rectangle_filled_with_colors(
            [x0, x1, x2, x3], [arcade.color.GRAY] * 4
        )
        shape_list.append(base)

        # Make centre line - in between lanes.
        cline_block_len = 5
        cline_block_width = 1

        road_start_midpoint = (road.a.start + road.b.end) / 2
        road_length = np.linalg.norm(a_vec)
        road_direction = a_vec / road_length
        perp_direction = perp_vec / np.linalg.norm(perp_vec)

        block_starts = np.arange(0, road_length, cline_block_len * 1.5)
        block_ends = np.arange(cline_block_len, road_length, cline_block_len * 1.5)

        if block_ends.shape[0] < block_starts.shape[0]:
            block_ends = np.concatenate([block_ends, [road_length]])

        for block_start, block_end in zip(block_starts, block_ends):
            cline_x0 = road_start_midpoint + block_start * road_direction
            cline_x1 = road_start_midpoint + block_end * road_direction

            cline_shape = arcade.create_rectangle_filled_with_colors(
                [
                    cline_x0 - perp_direction * cline_block_width * 0.5,
                    cline_x1 - perp_direction * cline_block_width * 0.5,
                    cline_x1 + perp_direction * cline_block_width * 0.5,
                    cline_x0 + perp_direction * cline_block_width * 0.5,
                ],
                [arcade.color.WHITE] * 4,
            )
            shape_list.append(cline_shape)

        return shape_list


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

    window.scene.add_road(
        create_road(np.array([5, 10]), road_length=80, lane_separation=10)
    )
    window.scene.add_road(
        create_road(np.array([15, 30]), road_length=84, lane_separation=8)
    )
    window.scene.add_road(
        create_road(np.array([85, 50]), road_length=-40, lane_separation=8)
    )

    window.run()
