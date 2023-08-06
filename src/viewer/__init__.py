import arcade
import arcade.color


class JunctionsWindow(arcade.Window):
    def __init__(self):
        screens = arcade.get_screens()
        super().__init__(800, 800, "Junctions", screen=screens[0])
        self.background_color = arcade.color.BUD_GREEN

    def on_draw(self):
        self.clear()


def run():
    window = JunctionsWindow()
    window.run()
