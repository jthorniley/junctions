from dataclasses import dataclass
from enum import Enum
from typing import Generic, Iterable, TypeAlias, TypeVar

from junctions.types import Junction

T = TypeVar("T", bound=Junction)


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
    junction: T
    can_commit: bool

    def commit(self) -> None:
        ...


class NetworkBuilder:
    def propose(
        self, junction_cls: type[T], constraints: Iterable[Constraint]
    ) -> Proposal[T]:
        ...
