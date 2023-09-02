# Simulating vehicles through the network

Vehicles are the main agents in the simulation. A vehicle's state
consists mainly of its position in the network, i.e. which lane
it is on, and a position on that lane.

## Moving around the map and lane priority

Recall the logical form of the connectivity map: directed edges or 
_lanes_ which are connected at vertices. Each vertex consists of zero
or more _connections_ which are pairs of lanes which are connected
from end-to-start.

Each vehicle is simulated moving along a lane. When it reaches the end
of the current lane it picks a connection (if there is one) which will
move it (usually immediately) to the start of the next lane.

Some lanes will physically conflict, for example at junctions like 
T-junctions, the lanes emerging from the side cross over the main road
lanes.

In order to prevent collisions between vehicles, they can be prevented
from crossing immediately into a new lane by putting a _wait_ flag on the
connection. When a vehicle tries to cross a connection with a _wait_
flag, it has to stop on its current lane until the connection is clear.




Furthermore when is switches to lanes in junctions (e.g. T-Junctions) 
we need to avoid collisions as the lanes cross each other. This is 
achieved by setting a flag called _wait_ on lane connections as 
appropriate - when a vehicle tries to cross such a connection, instead
of moving across immediately it has to wait until the flag is cleared.

## Speed limits

Each lane is given a speed limit, and normally a vehicle moves
along the lane at that speed limit.

It's fairly arbitrary but its probably easiest to think of the
dimensions and speeds in terms of meters and meters/second. So a lane
separation of 5 means a 5-meter wide road. A speed of 11 means 11 m/s.

For reference some speed limits close to common real world values:

| m/s | k/mh | mph |
| --- | ---- | --- |
|   6 |   22 |  14 |
|   9 |   32 |  20 |
|  14 |   50 |  31 |
|  22 |   79 |  50 |
|  28 |  101 |  63 |

## Vehicle dynamics

So to model the vehicle dynamics, assume the following prerequisites:

* We know which lane the vehicle is on.
* We know the length of that lane (as in distance along the curve, so
  for arcs that would be $r\theta$).
* We know the speed limit of that lane.

On each time step with a given change in time $\Delta t$, apply the _MoveVehicles_ algorithm.

Algorithm: _MoveVehicles_

1. For each vehicle in the simulation (with index $i$)
    1. Retrieve the corresponding speed limit for the lane the
       vehicle is on: $s_i$
    2. Calculate the movement of the vehicle: $m_i = s_i \Delta t$
    3. Calculate a new lane position: $l_i(t+\Delta t) = l_i(t) + m_i$
    4. If the new lane position is greater than the total lane length,
       apply the _TransitionToNewLane_ algorithm.

Algorithm: _TransitionToNewLane_

1. Given a vehicle $i$ which has a lane position $l_i(t)$ greater than
   the current lane length $L$.
2. Invert the time step to find the amount of time the vehicle was
   past the end of its lane:
   $$t_{excess} = \frac{l_i(t)-L}{s_i}$$
3. Choose a new lane $l'_i$ at random from the set of lanes connected
   to $l_i$ in the network.
   1. If there are no lanes connected, remove the vehicle from 
      the simulation.
5. Calculate the lane position on the new lane using the speed limit
   of the new lane: $l'_i(t) = s'_i t_{excess}$