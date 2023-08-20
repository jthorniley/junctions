from __future__ import annotations

import os
from io import BytesIO
from unittest import mock

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
    return pyglet.window.Window(200, 200, visible=False)


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
                assert sse < 10, "screenshot data diverged"
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
    NetworkRenderer(network).draw()

    # THEN the network is as expected
    reference_render.assert_screenshots_match()


@pytest.mark.skipif(SKIP_RENDERING_TESTS, reason="SKIP_RENDERING_TESTS env set")
def test_render_change_in_network(reference_render: ReferenceRender):
    # GIVEN a network with a road junction
    network = Network()

    # AND a network renderer
    network_renderer = NetworkRenderer(network)

    # WHEN I add the junction after the renderer is created
    network.add_junction(RoadFactory.build())

    # AND render it
    network_renderer.draw()

    # THEN the network is as expected
    reference_render.assert_screenshots_match()


@pytest.mark.skipif(SKIP_RENDERING_TESTS, reason="SKIP_RENDERING_TESTS env set")
def test_render_change_in_network_only_if_necessary(reference_render: ReferenceRender):
    """This tests that the network renderer only refreshes its shape batch
    when necessary (i.e. if the underlying network has changed)
    """
    # GIVEN a network with a road junction
    network = Network()

    # AND a network renderer
    network_renderer = NetworkRenderer(network)

    with mock.patch.object(
        network_renderer, "_add_junction", side_effect=network_renderer._add_junction
    ) as add_junction:
        # WHEN I add the junction after the renderer is created
        network.add_junction(RoadFactory.build())

        # AND render it
        network_renderer.draw()

        # THEN add junction is called in the renderer
        add_junction.assert_called_once_with("road1", network.junction_lookup["road1"])
        add_junction.reset_mock()

        # AND WHEN I render it again
        network_renderer.draw()

        # THEN no new shapes need to be created
        add_junction.assert_not_called()
        add_junction.reset_mock()

        # AND WHEN I add another junction and render
        network.add_junction(RoadFactory.build())

        # AND render it
        network_renderer.draw()

        # THEN the junctions are added again
        add_junction.assert_has_calls(
            [
                mock.call("road1", network.junction_lookup["road1"]),
                mock.call("road2", network.junction_lookup["road2"]),
            ]
        )

    reference_render.assert_screenshots_match()
