# Joining junctions into a network

Having some simple junction primitives (straight roads and arcs)
and event a composite junction (a T-junction) - we need a way to
combine these into a road network that connects points together.

Simply by placing junctions "next to" each other in physical space
we have implied a network:

![](images/t-junc.png)

However, its also useful to computationally represent the connectivity
between junctions. If we want to later simulate vehicles traversing the
network, it would generally be better to have a map of the logical
connections between junctions rather than rely on the physical layout
when vehicles need to cross the boundaries between junctions.
Similarly, a logical connectivity map would be useful to implement
things like path-planning.

## Representing connectivity on top of junction primitives

The junction primitives we have are defined in terms of two or more
lanes, generally one going in each direction. The lanes are directional,
so in general each lane is going to have an "in" and and "out" point.
A junction is therefore going to have a collection of implicitly matched
in and out points. 

For example in this illustration:

* Label the junction $\mathrm{J1}$
* It has two lanes $\mathrm{A}$ and $\mathrm{B}$, or if we need to 
  disambiguate them from another junction call them 
  $\mathrm{J1A}$ and $\mathrm{J1B}$.
* Each lane has an in and and out node, $\mathrm{J1A_{in}}$, $\mathrm{J1A_{out}}$ etc.


![](images/in-out.png)


To construct a network, we need to connect the lanes together in an
orientation that vehicles can traveerse, in other words, each 
connection will be between one lanes end node and the start node of
another lane (in a different junction).

For example, given a network of three junctions (J1 is a road and
J2 and J3 are arcs):

![](images/network-1.png)

Note first that the connectivity network here will split into two
disconnected subgraphs - one for the A lanes and one for the B lanes,
as in this example there is no way to loop round to the other set
of lanes.

The A-lane network has the J1A lane, with its end connected to
the start of J2A and J3A, represented by the extra white connecting
lines:

![](images/network-derived.png)

This is a directed acyclic graph (DAG) or network. We'll use the
term _vertex_/_vertices_ to refer to the points on this graph,
and _edge(s)_ to refer to the links between the vertices.

The edges in this graph come in two forms - either a _lane_ that
corresponds to the lanes modelled in our existing junction primitives,
or a _join_ (white line in the figure) which is a connector between
two lanes. A join always starts at a lane end vertex and ends at a
lane start vertex.