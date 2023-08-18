# Simulating traffic junctions with Python

I am interested in whether I can simulate traffic flowing through
junctions in various ways using some simulations.

* What junctions achieve the most throughput
* What is the effect of splitting and merging lanes
* What is the effect of moving people to public transport, active travel
* etc etc

## The simplest junction

The simplest junction is no junction - just a road with vehicles going
back and forwards.

We can name two lanes $a$ and $b$ and assume that vehicles will one
day traverse them from start to end. 

The lane start is a 2D coordinates $a_0$ (or $b_0$)
and end at coordinates $a_1$ (or $b_1$). In the diagram below we also
label the road length $l$ and separation $s$ (being the distance
in-between the two lanes).

![](images/a-b.png)
