from dataclasses import dataclass
from enum import Enum
from typing import Generic, Iterable, TypeAlias, TypeVar, cast

import numpy as np
from pyglet.math import Vec2

from junctions.network import LaneRef, Network
from junctions.types import Junction, Road

T = TypeVar("T", bound=Junction)


class InvalidConstraintError(ValueError):
    pass


class CannotCommitError(ValueError):
    pass


class Terminal(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


@dataclass
class ConnectTerminal:
    # Terminal to constraint to on the other junction
    other_terminal: Terminal
    # Identify the other junction
    other_juction: str


@dataclass
class NotConnected:
    # Point in space for unconnected terminal
    point: tuple[float, float]


Constraint: TypeAlias = ConnectTerminal | NotConnected


@dataclass
class ProposedConnection:
    # connections for proposed junction - from and
    # to either an existing lane (specified by LaneRef)
    # or to a lane in the new junction (specified by
    # lane string only - we don't know the junction label
    # yet)
    from_lane: LaneRef | str
    to_lane: LaneRef | str


@dataclass
class Proposal(Generic[T]):
    network: Network
    junction: T
    connections: Iterable[ProposedConnection]
    can_commit: bool  # TODO this should be called something else

    def commit(self, label: str | None = None) -> None:
        if not self.can_commit:
            raise CannotCommitError()

        label = self.network.add_junction(self.junction, label)

        for connection in self.connections:
            from_lane = connection.from_lane
            if isinstance(from_lane, str):
                from_lane = LaneRef(label, from_lane)

            to_lane = connection.to_lane
            if isinstance(to_lane, str):
                to_lane = LaneRef(label, to_lane)

            self.network.connect_lanes(from_lane, to_lane)


class NetworkBuilder:
    def __init__(self, network: Network) -> None:
        self._network = network

    def _get_terminal_bearing(self, junction_label: str, terminal: Terminal) -> float:
        junction = self._network.junction(junction_label)

        match junction:
            case Road(bearing=bearing):
                match terminal:
                    case Terminal.UP:
                        return bearing
                    case Terminal.DOWN:
                        # Attaching to the start of the terminal,
                        # so our bearing will be opposite to the
                        # existing junction
                        return (bearing + np.pi) % (np.pi * 2)
                    case _:
                        raise InvalidConstraintError()

            case _:
                raise NotImplementedError()

    def _get_terminal_point(self, junction_label: str, terminal: Terminal) -> Vec2:
        junction = self._network.junction(junction_label)

        match junction:
            case Road():
                match terminal:
                    case Terminal.UP:
                        lane = junction.lanes["a"]
                        return lane.end
                    case Terminal.DOWN:
                        # In this case we are attaching our "DOWN" to another
                        # junction's "DOWN" - so this new junction will need
                        # to be rotated round so that it's a starts at the end
                        # of the other junctions b (and is connected appropriately)
                        lane = junction.lanes["b"]
                        return lane.end
                    case _:
                        raise InvalidConstraintError()
            case _:
                raise NotImplementedError()

    def _propose_road(self, constraints: Iterable[Constraint]) -> Proposal[Road]:
        match constraints:
            case [NotConnected(point1), NotConnected(point2)]:
                bearing = np.arctan2(point2[0] - point1[0], point2[1] - point1[1])
                origin = point1
                # TODO: this is just fixed??
                lane_separation = 5
                length = Vec2(*point1).distance(Vec2(*point2))

                return Proposal(
                    self._network,
                    Road(point1, bearing, length, lane_separation),
                    connections=(),
                    can_commit=True,
                )

            case [
                ConnectTerminal(other_terminal, other_junction),
                NotConnected(point),
            ] | [NotConnected(point), ConnectTerminal(other_terminal, other_junction)]:
                bearing = self._get_terminal_bearing(other_junction, other_terminal)
                origin = self._get_terminal_point(other_junction, other_terminal)
                lane_separation = self._network.junction(other_junction).lane_separation

                picked = Vec2(*point) - origin
                length = np.sin(bearing) * picked.x + np.cos(bearing) * picked.y

                if length < 0:
                    return Proposal(
                        self._network,
                        Road((origin.x, origin.y), bearing, 0, lane_separation),
                        connections=(),
                        can_commit=False,
                    )

                match other_terminal:
                    case Terminal.UP:
                        # Connect the other junction's a to our a, and our b to the
                        # other junction's b
                        connections = [
                            ProposedConnection(LaneRef(other_junction, "a"), "a"),
                            ProposedConnection("b", LaneRef(other_junction, "b")),
                        ]
                    case Terminal.DOWN:
                        connections = [
                            ProposedConnection(LaneRef(other_junction, "b"), "a"),
                            ProposedConnection("b", LaneRef(other_junction, "a")),
                        ]
                    case _:
                        raise InvalidConstraintError()

                return Proposal(
                    self._network,
                    Road((origin.x, origin.y), bearing, length, lane_separation),
                    connections=connections,
                    can_commit=True,
                )

            case _:
                raise NotImplementedError()

    def propose(
        self, junction_cls: type[T], constraints: Iterable[Constraint]
    ) -> Proposal[T]:
        if junction_cls is Road:
            return cast(Proposal[T], self._propose_road(constraints))

        raise NotImplementedError()
