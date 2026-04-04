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

$$F = - \frac{\partial E}{\partial \bold{R}} = - \frac{\partial f_{\textrm{NN}}(\bold{R}, \scr{M}; \bold{w})}{\partial \bold R} \in \RR^{N \times 3}.$$
The advantage of this approach is that the resulting force field is *conservative*, 
which promotes energy conservation over the simulation lifetime.


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
makes predictions that satisfy both properties, and we'll examine 
their mathematical and computational aspects in this post.
A quick plug: in January 2025, we released 
[OpenEquivariance](https://github.com/vbharadwaj-bk/OpenEquivariance) to accelerate equivariant 
graph neural networks by an order of magnitude. 

There are lots of online resources on equivariant graph neural networks. I recommend
[Tensor Field Networks](https://arxiv.org/abs/1802.08219), one of the first papers in this space,
for an accessible and rigorous take. Slides from 
[Tess Smidt](https://blondegeek.github.io/) are very useful, but I find them a bit difficult
to parse due to my lack of domain knowledge. I'm not a chemist, so I'm going to give you an 
explanation that requires no prerequisite besides a strong mathematical background. Skip ahead
if you're familiar with these networks already. 

## An Intuition for Equivariance
Let's formalize our definition of equivariance a little further. Suppose we want to design an
function $f: \RR^{3} \rightarrow \RR$ so that any rotation in the input vector produces no change
in the output scalar. We'll let $G=O(3)$ be the [group](https://en.wikipedia.org/wiki/Group_(mathematics))
of rotations including reflection in 3D space, and we'll define $\bold{R}(g) \in \RR^{3 \times 3}$ 
as the canonical [3D rotation matrix](https://en.wikipedia.org/wiki/Rotation_matrix#In_three_dimensions)
for any rotation $g \in G$. In this case, the equivariance property on $f$ is 

$$f\paren{\bold{R}(g) \cdot \bold{x}} = f(\bold{x})\quad\forall \bold{x} \in \RR^{3}, g \in G.$$

Perfect. Say, now, that $f$ predicts a 3D vector instead of a scalar, i.e. its signature is
$f: \RR^3 \rightarrow \RR^3$. Here too, we have one natural definition of equivariance:

$$f\paren{\bold{R}(g) \cdot \bold{x}} = \bold{R}(g) \cdot f(\bold{x})\quad\forall \bold{x} \in \RR^{3}, g \in G.$$

In other words, rotations on the function input convert to rotations on the function output. So far, so good.

However: $f$ in our case will represent an intermediate layer of a deep graph neural network, which derives
much of its expressive capability by operating on input / output vectors of arbitrary dimensionality. What
does equivariance mean when $f$ has the signature $f: \RR^m \rightarrow \RR^n$, where $n, m > 3$? 

We need some additional machinery to construct a general definition of an equivariant function: specifically,
define a real representation as follows:

!!! definition "Representation"
    A (real) representation is a map $D: G \rightarrow \RR^{n \times n}$ that preserves the group structure
    of $G$ under matrix multiplication:
    $$D(g \circ h) = D(g) \cdot D(h),$$
    where $\circ$ is the group operator. 

In our case, ever rotation is mapped to a square matrix of arbitrary dimension that *represents* the group
element. If you multiply two of these matrices together, you get a third matrix representing the rotation
that is a composition of the two input rotations. Armed with this definition, we have the following general 
definition:

!!! definition "Equivariant Function"
    A function $f: \RR^n \rightarrow \RR^m$ is equivariant with respect to representations 
    $D_{\textrm{in}}: G \rightarrow \RR^{n \times n}$ and
    $D_{\textrm{out}}: G \rightarrow \RR^{m \times m}$ iff 

    $$D_{\textrm{out}}\paren{g} \cdot f \paren{\bold{x}} = f\paren{D_{\textrm{in}}\paren{g} \cdot \bold{x}}$$

