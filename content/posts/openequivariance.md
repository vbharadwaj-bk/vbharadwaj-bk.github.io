---
Title: "Accelerating Equivariant Neural Networks" 
Date: 2026-03-22
Category: computer-science 
Summary: A deep-dive into OpenEquivariance, our Clebsch-Gordon tensor product accelerator.  
thumbnail: "images/blog/cg_tensor_product.png" 
---
An *equivariant graph neural network* preserves certain geometric relations between its input
and output. We'll focus on 3D rotation-equivariant neural networks in this post, which have the
following property:

> **Rotation-Equivariance**: If the input rotates, the output stays the same or rotates compatibly.

Why are rotation-equivariant networks useful? Suppose you're a computational chemist researching
new ways to build efficient batteries. Actually mixing chemicals and building a candidate battery
is expensive, so you'd like to narrow down the list of formulations quickly using molecular
dynamics simulations. You put a configuration of atoms into the simulator and, by calculating the
force on each atom repeatedly over many timesteps, you can predict the chemistry of the system
as it evolves over time.

That force prediction is a difficult task, though. Atomic forces are governed by quantum mechanical
interactions that are traditionally approximated by methods like 
[density functional theory (DFT)](https://en.wikipedia.org/wiki/Density_functional_theory). DFT is,
in general, accurate but slow. 

Here's an alternate method: let the atom positions be $\bf{R} \in \RR^{x}$ 



In January 2025, we released [OpenEquivariance](https://github.com/vbharadwaj-bk/OpenEquivariance).


!TEMPLATE!
<div class="row">
    <div class="col-2">
    </div>
        <div class="col-8 card border-0 bg-white p-1 mb-3">
        {{ figure(path="images/blog/atomic_gnn.png",title="Pipeline for molecular property prediction.", class="img-fluid rounded z-depth-1", zoomable=True) }}
        <div class="caption">
        Atomic graph neural networks take in atom positions and metadata. They emit predictions of 
        total system energy and the force on each atom.
        </div>
</div>
<div class="col-2">
</div>
</div>
!TEMPLATE!