---
Title: "Accelerating Equivariant Neural Networks" 
Date: 2026-03-22
Category: computer-science 
Summary: A deep-dive into OpenEquivariance, our Clebsch-Gordon tensor product accelerator.  
thumbnail: "images/blog/cg_tensor_product.png" 
latex_macro_file: 'content/latex/common_macros.yaml'
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

Here's an alternate method: store the $N$ atom positions in a matrix $\bold{R} \in \RR^{N \times 3}$,
and let $\scr{M}$ represent metadata about the atoms (e.g. species). We feed both to a deep neural network
that will predict the total potential energy of the system:
$$E = f_{\textrm{NN}}\paren{\bold{R}, \scr M; \bold{w}},$$

where $\bold{w}$ contains trainable weights that parameterize the network. To get the atomic forces,
we can calculate

$$F = - \frac{\partial E}{\partial \bold{R}} = - \frac{\partial f_{\textrm{NN}}(\bold{R}, \scr{M}; \bold{w})}{\partial \bold R}.$$
The advantage of this approach is that the force field is *conservative*, which promotes energy conservation 
over the simulation lifetime.


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
The energy of a molecule doesn't change when you rotate it in space. It also shouldn't change
if the order of the position vectors in $\bold{R}$ changes. A rotation-equivariant graph neural network
satisfies both properties, and we'll examine their mathematical and computational aspects in this post.
A quick plug: in January 2025, we released 
[OpenEquivariance](https://github.com/vbharadwaj-bk/OpenEquivariance) to accelerate equivariant 
graph neural networks by an order of magnitude. 

There are lots of online resources on equivariant graph neural networks. I recommend
[Tensor Field Netwwrks](https://arxiv.org/abs/1802.08219), one of the first papers in this space,
for an accessible yet rigorous take. 

