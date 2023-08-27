from __future__ import annotations

import os
from io import BytesIO

import pyglet
import pytest
from imageio import imwrite
from imageio.v3 import imread
from junctions.network import Network
from viewer.network_renderer import NetworkRenderer

from tests.junctions.factories import ArcFactory, RoadFactory

SKIP_RENDERING_TESTS = bool(os.environ.get("SKIP_RENDERING_TESTS"))


@pytest.fixture(scope="session")
def pyglet_win():
    win = pyglet.window.Window(200, 200, visible=False)
    pyglet.gl.glClearColor(0, 0, 0, 1)
    return win


class ReferenceRender:
    def __init__(self, request: pytest.FixtureRequest):
        self.request = request

    def assert_screenshots_match(self):
        buffer = BytesIO()
        pyglet.image.get_buffer_manager().get_color_buffer().save(
            "screenshot.png", buffer
        )
        buffer.seek(0)
        screenshot_path = (
            self.request.path.parent
            / "screenshots"
            / f"screenshot.{self.request.node.name}.png"
        )

        if screenshot_path.exists():
            orig_data = imread(buffer)
            data = orig_data.astype(float)
            compare = imread(screenshot_path).astype(float)
            try:
                assert data.shape == compare.shape
                sse = ((data - compare) ** 2).sum()
                # There's quite a high tolerance for change in this, as any pixel
                # diverging potentially adds to a lot
                assert sse < 150000, "screenshot data diverged"
            except AssertionError:
                imwrite(
                    screenshot_path.parent
                    / f"failed-screenshot.{self.request.node.name}.png",
                    orig_data,
                )
                raise

        else:
            # save screenshot if it doesn't exist - by definition, the test will pass
            screenshot_path.parent.mkdir(exist_ok=True)
            screenshot_path.write_bytes(buffer.getvalue())


@pytest.fixture
def reference_render(request, pyglet_win: pyglet.window.Window):
    pyglet_win.clear()

    yield ReferenceRender(request)


@pytest.mark.skipif(SKIP_RENDERING_TESTS, reason="SKIP_RENDERING_TESTS env set")
@pytest.mark.parametrize("_fuzz", range(20))  # implicitly 20 random seeds
def test_render_road_arc(reference_render: ReferenceRender, _fuzz):
    # GIVEN a network with a road and arc junction
    network = Network()
    network.add_junction(RoadFactory.build())
    network.add_junction(ArcFactory.build())

    # WHEN I render the network
    NetworkRenderer(network.junction_lookup).draw()

    # THEN the network is as expected
    reference_render.assert_screenshots_match()
