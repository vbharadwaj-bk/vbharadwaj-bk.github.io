---
Title: Algorithms for Fundamental Cycle Balancing 
Date: 2022-05-12 
Category: math 
Summary: Some notes about signed graphs and fundamental cycles.
thumbnail: "images/blog/cycle_balancing.svg"
toc:
  sidebar: true
---
Suppose we have a **signed graph** $G = (V, E)$ where each node represents
a member in a parliament. All members of the parliament will vote
up (1) or down (0) on some measure. Every edge is annotated 
with either $+$ or $-$, indicating whether two members prefer to 
agree ($+$) or disagree ($-$) with each other on their positions. If you'd
like, imagine that two members who are fighting prefer
to disagree on their votes, while two strong friends
prefer to agree on their votes. The goal of the **fundamental cycle balancing problem** is 
to assign each node a 0 / 1 label such that all of the edge
constraints on agreement / disagreement are respected. 

## Background on Cycle Balancing 
We can easily construct graphs that are impossible to label without 
violating at least one edge
constraint (consider a triangle graph with exactly one negative edge).
In practice, we settle on minimizing 
the number of violated constraints. The minimum number of violated 
constraints for a signed graph (across all possible labellings) is called 
the **frustration index**. Finding the exact value of the frustration 
index turns out to be NP-hard. We define a **balanced graph** as a
signed graph where all edge constraints are satisfied, so the frustration
index is the minimum number of edges whose signs we must flip to obtain
a balanced state.

A [2021 Supercomputing paper](https://dl.acm.org/doi/10.1145/3458817.3476153) (Alabandi et al.) does a pretty good job introducing this 
problem. It shifts the goalposts a bit; instead of computing the
frustration index, it seeks to sample the _frustration cloud_, the set
of **minimally balanced** states of the graph. A signed graph with some
subset of edges $Q$ with flipped labels is called
**minimally balanced** iff:

1. The graph is balanced 
2. No strict subset $P \subset Q$ of those edges flipped in the
original graph yields a balanced graph. 

Generating a minimally balanced state is simple: pick any
spanning tree of the graph and declare that all edges in that spanning
tree must satisfy their edge constraints. Then loop through all remaining
edges of the graph to determine whether their constraints are satisfied
or violated. The SC21 paper proposes GraphB+, an parallel algorithm 
to sample the frustration cloud. It samples spanning trees on several GPUs 
and uses a traversal algorithm to identify the number of constraints
violated by obeying all constraints in each tree.

The GraphB+ algorithm is **not optimal**. Here are some notes: 

1. Once the GraphB+ algorithm samples a spanning tree, it
does more work than necessary to identify violated constraints. Once
we declare that every constraint in the spanning tree is obeyed, we can
label each node to respect those choices by arbitrarily
assigning 0 to the root and traversing the rest of the tree. From there, 
it suffices to loop over all edges not in the tree, read off the labels
of their endpoints (along with the sign of the edge), and count up
the number of violated constraints. GraphB+, by contrast, uses a more
complicated cycle traversal algorithm to identify each violated constraint,
along with potentially unecessary metadata on each vertex.

2. Is the frustration cloud just a tractable approximation to 
the frustration index (by averaging over the frustration 
values of samples)? 
Interestingly, the algorithm used to 
generate the spanning trees (see this 
[other paper](https://arxiv.org/pdf/2009.07776.pdf) on 
fundamental cycle balancing) appears to affect the results. Can we 
develop algorithms to compute an approximate frustration index that 
do not rely on the frustration cloud?

    In the remainder of this post, we will abandon the frustration cloud
    and consider efficient algorithms to compute the frustration index
    directly. 

3. Computing the frustration index is really a special case 
of the **graph bi-partitioning**
problem with binary $+1$ / $-1$ weighted edges. The similarity is obvious: 
we want to develop a cut in the graph such that the minimum number of $+$ edges cross the cut. Here are a couple of major differences:

    a. Most formulations of graph partitioning (and most software
packages for 
graph partitioning, such as METIS) do not allow negative weight edges,
whereas we require them for fundamental cycle balancing. In other
words, we need to discourage some edges from crossing the cut while
*encouraging* others to cross the cut.

    b. Graph bipartitioning typically aims to equalize the sum of vertex
weights in each side of the partition, whereas no such constraint
exists in fundamental cycle balancing (although one could be 
introduced)

## Relation to Graph Partitioning
Why can't we use a graph partitioner to solve this problem? Fair question; given how similar this problem is to graph partitioning,
we might take a signed graph, assign weights to the edges 
according to some rule, and run a graph partitioner to bisect the graph. 
The issue here? It is difficult (maybe impossible! 
I'm thinking about proving it) to construct a weight 
assignment to the edges so that the graph partitioner
optimizes an objective consistent with the cycle balancing problem. 

Suppose we tried the following mapping: given a signed
graph with edges labelled $-1$ or $+1$, replace the signs according
to the map 

$$-1 \mapsto 1$$

$$+1 \mapsto 2$$

The hope is that the graph partitioner will penalize the original $+1$ 
edges that cross the cut disproportionately compared to 
the original negative weight edges. Then consider
the following signed graph on four vertices shaped like the 
letter "N":

!TEMPLATE!
<div class="row">
    <div class="col-4">
    </div>

        <div class="col-4 card border-0 bg-white p-1 mb-3">
        {{ figure(path="images/blog/cycle_balancing.svg",title="An Example Signed Graph") }}
        </div>

    <div class="col-4">
    </div>
</div>
!TEMPLATE!

The frustration index of this graph is 0: we assign 1 to $B$ and $C$,
and 0 to $A$ and $D$, corresponding to a partition $P^*= [(B, C), (A, D)]$. 

Now let's take a look at our graph partitioner's behavior
under this mapping. $P^*$ has two edges of weight +1 under our mapping
that cross the cut, yielding a cost of 2. Now consider the alternate
partition $\hat P = [(A, B), (C, D)]$. To our graph partitioner, $\hat P$ also has a cost of 2, since the positive weight edge crossing the partition has a cost of 2 
under our mapping. But the frustration of $\hat P$ is 3,
since every constraint is violated! In other words, our graph
partitioner will not distinguish between these two partitions
in the transformed problem, while one is clearly optimal in
the original problem. Increasing the weight assigned to positive
edges would cause other undesirable effects, such as biasing
the partitioner to treat positive edge constraints as more important
than the negative ones. 

## Computing the Frustration Index 
From the counterexample above, existing graph partitioning 
software might not accurately capture
the frustration index. Still, we might be able to adapt 
*techniques* from the graph partitioning problem to solve 
our cycle balancing problem. These techniques include:

- Kernighan-Lin or Fiduccia-Mattheyses Heuristics: Start with
some partition and iteratively refine it according to some objective
function 

- Spectral clustering: Find the second smallest eigenvalue /
eigenvector pair of the graph Laplacian. This 
[paper](https://arxiv.org/pdf/1701.01394.pdf) appropriately modifies
the graph Laplacian to account for negative weight edges in signed
graphs.

- Hierarchical Coursening / Refinement: Solve the problem on a
coursened approximation of the graph, then refine the solution
successively at finer resolutions

You could also attempt to sample spanning trees, as GraphB+ does,
without the baggage of counting violated constraints by cycle
traversal mentioned above. An approximate frustration index
could be computed by averaging the frustrations induce by each of
the trees. 

We want these these techniques to be parallelizable so we can analyze
graphs with millions of vertices and billions of edges. 

## CS267 Class Projects!
I outlined some of these ideas to students in the 2022 version of 
[CS267: Applications of Parallel Computers](https://sites.google.com/lbl.gov/cs267-spr2022). Several of them chose to work on this problem
for their final projects! I hope it made for fun and interesting work.
