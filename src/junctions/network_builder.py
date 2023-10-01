from dataclasses import dataclass
from enum import Enum
from typing import Generic, Iterable, TypeAlias, TypeVar, cast

from pyglet.math import Vec2

from junctions.network import Network
from junctions.types import Junction, Road

T = TypeVar("T", bound=Junction)


class InvalidConstraintError(ValueError):
    pass


class Terminal(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


@dataclass
class ConnectTerminal:
    # Which terminal on the new junction to constraint
    this_terminal: Terminal
    # Terminal to constraint to on the other junction
    other_terminal: Terminal
    # Identify the other junction
    other_juction: str


@dataclass
class NotConnected:
    # Which terminal to constrain
    this_terminal: Terminal
    # Point in space for unconnected terminal
    point: tuple[float, float]


Constraint: TypeAlias = ConnectTerminal | NotConnected


@dataclass
class Proposal(Generic[T]):
    network: Network
    junction: T
    can_commit: bool

    def commit(self) -> None:
        ...


class NetworkBuilder:
    def __init__(self, network: Network) -> None:
        self._network = network

    def _get_terminal_bearing(self, junction_label: str, terminal: Terminal) -> float:
        junction = self._network.junction(junction_label)

        match junction:
            case Road(bearing=bearing):
                return bearing

            case _:
                raise NotImplementedError()

    def _get_terminal_point(self, junction_label: str, terminal: Terminal) -> Vec2:
        junction = self._network.junction(junction_label)

        match junction:
            case Road():
                lane = junction.lanes["a"]
                match terminal:
                    case Terminal.DOWN:
                        return lane.start
                    case Terminal.UP:
                        return lane.end
                    case _:
                        raise InvalidConstraintError()
            case _:
                raise NotImplementedError()

    def _propose_road(self, constraints: Iterable[Constraint]) -> Proposal[Road]:
        up_constraint: Constraint | None = None
        down_constraint: Constraint | None = None

        # Check constraints
        for constraint in constraints:
            match constraint.this_terminal:
                case Terminal.UP:
                    up_constraint = constraint
                case Terminal.DOWN:
                    down_constraint = constraint
                case _:
                    raise InvalidConstraintError()

        if not up_constraint or not down_constraint:
            raise InvalidConstraintError()

        # Algorithm
        # 1. determine bearing - if constrained to other terminals must
        #    match bearing of those terminals. If not can be determined
        #    from each end.
        # 2. determine length -

        match down_constraint:
            case ConnectTerminal(_, other_terminal, other_junction):
                bearing = self._get_terminal_bearing(other_junction, other_terminal)
                origin = self._get_terminal_point(other_junction, other_terminal)
                lane_separation = self._network.junction(other_junction).lane_separation

                match up_constraint:
                    case NotConnected(point=point):
                        point_vec = Vec2(*point)
                        length = origin.distance(point_vec)
                        return Proposal(
                            self._network,
                            Road(
                                (origin.x, origin.y), bearing, length, lane_separation
                            ),
                            can_commit=True,
                        )
                    case _:
                        raise NotImplementedError()
            case _:
                raise NotImplementedError()

    def propose(
        self, junction_cls: type[T], constraints: Iterable[Constraint]
    ) -> Proposal[T]:
        if junction_cls is Road:
            return cast(Proposal[T], self._propose_road(constraints))

        raise NotImplementedError()
