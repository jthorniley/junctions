# Network builder

A [network](./02-network.md) consists of a number
of junctions (each of which consists of one or more
lanes) and connections between the junctions/lanes.

Building a physically realistic network requires that the
connected lanes are placed end-to-start next to each other,
so that vehicles aren't unrealistically jumping from one 
lane to the next.

The network builder is a helper class to create a network
with connected lanes where lanes are guaranteed to be
placed in appropriate locations for their connectivity.

## Terminals

We'll refer to the connection points of _junctions_ (rather
than lanes) as terminals. For example, a road consists of
two lanes, and therefore four connection nodes (lane a,
start and end, and lane b, start and end). But at the 
level of the junction, a road has a start terminal and end
terminal, which we might connect to the start/end of another
road. 

Terminals are connection points and are used to constrain
the placement and parameters of junctions, but don't need
to be connected end-to-start like the nodes of lanes.

## Creating new junction

A new road can be constrained at one or both terminals to 
connect to another junction (we allow one terminal to be 
left unconnected).

If connecting at one end, the new road will take its bearing
from the terminal it is connecting to. If connecting at
both ends, the bearing of both terminals will need to
be the same, and they will need to be in line with each
other so that a straight road can connect them.

Similar logic applies for other junctions - arcs can 
connect at one or both terminals, and T-junctions have
up to three terminal connections.

## Proposing and committing a new junction

Given an existing network, we can specify a new junction
that isn't possible to construct within the constraints
described above. In order to let the network builder check
the constraints without modifying the network to become
invalid, there is a two-stage process. First the constraints
are checked and applied to create a new junction proposal,
and if that is valid we can choose whether or not to
"commit it" and update the network.

```python

network = Network()
network.add_junction(Road((0,0), length=50, lane_separation=5))

network_builder = NetworkBuilder()
proposal = network_builder.propose(Road, [
    ConnectTerminals(Terminal.START, "road1", Terminal.END),
    UnconnectedTerminal(Terminal.END, (100, 0))
])

assert proposal.can_commit  # Checks if the proposal is valid
proposal.commit(label="road2")
assert network.get_junction("road2") # Now added to network
```


