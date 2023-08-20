from io import BytesIO

import pyglet
import pytest
from imageio.v3 import imread


@pytest.fixture(scope="session")
def pyglet_win():
    return pyglet.window.Window(200, 200)


@pytest.fixture
def reference_render(request, pyglet_win: pyglet.window.Window):
    pyglet_win.clear()

    yield

    buffer = BytesIO()
    pyglet.image.get_buffer_manager().get_color_buffer().save("screenshot.png", buffer)
    buffer.seek(0)
    screenshot_path = request.path.parent / f"screenshot.{request.node.name}.png"

    if screenshot_path.exists():
        data = imread(buffer).astype(float)
        compare = imread(screenshot_path).astype(float)
        assert data.shape == compare.shape
        sse = ((data - compare) ** 2).sum()
        assert sse < 10, "screenshot data diverged"

    else:
        # save screenshot if it doesn't exist - by definition, the test will pass
        screenshot_path.write_bytes(buffer.getvalue())


@pytest.mark.usefixtures("reference_render")
def test_network_renderer():
    pyglet.shapes.Line(0, 0, 100, 100, 1).draw()
