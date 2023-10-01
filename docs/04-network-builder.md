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
level of the junction, a road has two _terminals_, which can
connect to terminals of other junctions.

A road junction is defined to have two terminals, `UP` and
`DOWN`. The `DOWN` terminal is the end with the `a`-lane
start and `b`-lane end, and the `UP` terminal is the other
end of the road.

An arc can be defined equivalently (logically it has the 
same terminals).

A T junction has an extra terminal which for the sake of
argument we will call `RIGHT` (a cross-roads junction
would also have a `LEFT`).

## Building junctions

Junctions are created by specifying where the terminals of
the junction should go, using either reference to existing
terminals of junctions already in the network, or by giving
explicit points (where we don't want to connect the terminal
of the new junction to any existing terminal).

### Road with both terminals unconnected

Given two vector coordinates $\vec{p}_{DOWN}$ and $\vec{p}_{UP}$
representing the "picked" coordinates where we want to place the
down and end terminals, we just define the road origin as
$\vec{o}=\vec{p}_{DOWN}$ and the road vector 

$$\vec{v}=\vec{p}_{UP}-\vec{p}_{DOWN}$$

The road parameters are its length $l=|\vec{v}|$ and bearing
$\theta=\arctan\frac{v_x}{v_y}$. We also need to determine the
lane separation either explicitly or using a default, as it
is not constrained by the two picked points.

### Road with one terminal connected to an existing junction

Assume that the connected terminal is `DOWN` and the 
unconstrained target point $\vec{p}_{UP}$ is as before a chosen
desired point for the `UP` terminal.

The bearing $\theta$ and origin $\vec{o}$ will be directly taken 
from the terminal that `DOWN` is connected to so that the road
lines up with the junction it has been specified to connect to.
We can also assume that the lane separation must be specified
by the junction/terminal that we are connecting to.

The problem is over-constrained in that the picked vector
for the road $\vec{p}_{UP}-\vec{o}$ may not have the same bearing
as the required $\theta$. Therefore we take the component of the
picked vector in line with $\theta$ - the road vector $\vec{v}$
is calculated with the dot product:

$$ \vec{v}=[\sin\theta, \cos\theta] \cdot (\vec{p}_{UP}-\vec{o}) $$

And then as before $l=|\vec{v}|$.

