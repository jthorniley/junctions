# Simulating traffic junctions with Python

I am interested in whether I can simulate traffic flowing through
junctions in various ways using some simulations.

* What junctions achieve the most throughput
* What is the effect of splitting and merging lanes
* What is the effect of moving people to public transport, active travel
* etc etc

## Environment set up

Install Python 3.11 or higher.

Install [Poetry](https://python-poetry.org/).

Configure virtual environment with poetry

    poetry install

## Running the simulation

There is a [Pyglet](https://pyglet.readthedocs.io/en/latest/index.html) based
UI that visualises what's going on. Once the Poetry virtual environment is
configured it should be possible to run it with:

    poetry run python -m viewer

(Tested on windows)

## Running the tests

It should be possible to run tests with

    poetry run pytest

This includes visual rendering tests which screenshot the results of the renderer
and compare them to pngs to check that the renderer is working. If necessary skip
them by setting the environment variable `SKIP_RENDERING_TESTS`

    env SKIP_RENDERING_TESTS=1 poetry run pytest   # Mac/Linux
    $env:SKIP_RENDERING_TESTS=1; poetry run pytest  # powershell

