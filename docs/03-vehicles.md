# Simulating vehicles through the network

Vehicles are the main agents in the simulation. A vehicle's state
consists mainly of its position in the network, i.e. which lane
it is on, and a position on that lane. The behaviour of vehicles
is defined by the following rules:

* Normally, a vehicle will just incrementally move along the current
  lane at a "speed limit" that is set corresponding to the lane.
* If a vehicle comes to the end of a lane it will have to pick one
  of the connected lanes to move on to.
* When a vehicle is moving onto a new lane, it will wait (set speed to
  zero) if that new lane is blocked because it is crossed by some higher
  priority lane with a vehicle on it.
* Vehicles behind stopped vehicles also have to stop and wait when they
  get close.

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
lane they are moving to. When a vehicle tries to cross a connection with 
a _wait_ flag set on the next lane, it has to stop on its current lane
until the connection is clear. (This doesn't affect vehicles already on
the target lane, which should continue moving to clear the lane).

### T-Junction lane priority

The principle with a T-junction is that traffic going straight on the
main road has priority, and traffic turning in or out of the side road
should wait for the lanes to be clear.

Looking at the T-junction schematic, we have three sections consisting
of two lanes each: the main road (straight road) with lanes 
_Ma_ and _Mb_ and the two branches - branch A (arc) _Aa_ and _Ab_, 
and branch B (another arc) with _Ba_ and _Bb_.

![](images/t-junction-labels.png)

We can define the wait condition to enter each lane based on the priority
of the main road:

* _Ma_ and _Mb_, and _Aa_ never have a wait condition
* _Ab_ waits if it is not clear on _Ma_, _Mb_ or _Bb_.
* _Ba_ waits if it is not clear on _Ma_.
* _Bb_ waits if it is not clear on _Ma_ or _Aa_.

### Lane switching algorithm

In order to choose which lane a vehicle moves on to, we first calculate
the wait flags for all the lanes in the simulation:

* For each lane L:
  * For each lane P in the set of lanes that have priority over L.
    * IF P contains a vehicle
    * OR any of the lanes feeding into P contain a vehicle, AND that
      vehicle would reach P before the time it would take for a vehicle
      to completely move through P
      * THEN set the wait flag for L
  * The wait flag is unset for L if none of the priority lanes P had
    a condition that set the wait flag as above.

When a vehicle reaches the end of its current lane, and the next step
would move it past the end:

* Pick a connected lane L at random to move onto.
* IF the wait flag is set on L, then the vehicle stops and waits at the end
  of its current lane. The choice of lane L is stored so that the vehicle
  will still wait for the wait flag on L to be cleared on the next iteration
  (rather than picking another lane and moving on to that).
* Otherwise, move onto L.

## Speed limits

Each lane is given a speed limit, and normally a vehicle moves
along the lane at that speed limit.

Though the simulation units could be anything, if we set the usual
distances measure to be meters (so specifying e.g. lane separation of
5 means 5 meters), then its natural to measure speeds in meters per
second - a speed of 11 means 11 m/s.

For reference some speed values in meters/second close to common real
world speed limits are:


| m/s | km/h | mph |
| --- | ---- | --- |
|   6 |   22 |  14 |
|   9 |   32 |  20 |
|  14 |   50 |  31 |
|  22 |   79 |  50 |
|  28 |  101 |  63 |


## Vehicle waiting and queuing

When a vehicle has to wait (due to wait flags as described above), it
will stop and thus block the lane. Vehicles behind cannot pass on the 
same lane so we define a separation rule - if a there is another vehicle
in front of the current vehicle within a chosen separation distance
(say 5 meters), then the vehicle stops and waits (i.e. we set its speed
to zero). This creates a queueing dynamic of vehicles waiting behind
each other if there is one in front.

