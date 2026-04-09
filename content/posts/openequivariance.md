---
Title: "Accelerating Rotation-Equivariant Networks" 
Date: 2026-03-22
Category: computer-science 
Summary: A deep dive into OpenEquivariance, our Clebsch-Gordon tensor product accelerator.  
thumbnail: "images/blog/cg_tensor_product.png" 
latex_macro_file: 'content/latex/common_macros.yaml'

toc:
  sidebar: True
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

!figure(images/blog/atomic_gnn.png, medium, "Pipeline for molecular property prediction.", "Atomic graph neural networks take in atom positions and metadata. They emit predictions of total system energy and the force on each atom.")

The energy of a molecule doesn't change when you rotate it in space. It also shouldn't change
if the order of the position vectors in $\bold{R}$ changes. A rotation-equivariant graph neural network
makes predictions that satisfy both properties, and we'll examine 
their mathematical and computational aspects in this post.
A quick plug: in January 2025, we released 
[OpenEquivariance](https://github.com/vbharadwaj-bk/OpenEquivariance) to accelerate equivariant 
graph neural networks by an order of magnitude. 

Much of this material is drawn from the [e3nn convolution tutorial](https://docs.e3nn.org/en/latest/guide/convolution.html),
[Lim and Nelson's introductory paper](https://arxiv.org/abs/2205.07362), and [Tensor Field Networks](https://arxiv.org/abs/1802.08219), a foundational paper in the space. Slides from 
[Tess Smidt](https://blondegeek.github.io/) are also very useful, but I find them a bit difficult
to parse due to my lack of domain knowledge. I'm not a chemist, so I'm going to give you a homegrown 
explanation that requires no prerequisite besides a strong linear algebra background. 
[Skip ahead](#openequivariance-turbocharging-cg-tensor-products) if you're a veteran and want details of our 
computational contributions. This material is adapted from our 
[paper](https://epubs.siam.org/doi/10.1137/1.9781611979084.3) describing OpenEquivariance. 

## An Intuition for Equivariance
Let's formalize our definition of equivariance a little further. Consider a 
function $f: \RR^{3} \rightarrow \RR$ such that any rotation in the input vector produces no change
in the output scalar. We'll let $G=SO(3)$ be the [group](https://en.wikipedia.org/wiki/Group_(mathematics))
of rotations excluding reflection in 3D space, and we'll define $\bold{R}(g) \in \RR^{3 \times 3}$ 
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

We need some additional machinery to construct a general definition of an equivariant function. Specifically,
define a real representation as follows:

!!! definition "Representation"
    A (real) representation is a map $\bold{D}: G \rightarrow \RR^{n \times n}$ that preserves the group structure
    of $G$ under matrix multiplication:
    $$\bold{D}(g \circ h) = \bold{D}(g) \cdot \bold{D}(h),$$
    where $\circ$ is the group operator. 

In our case, every rotation is mapped to a square matrix of arbitrary dimension that *represents* the group
element. If you multiply two of these matrices together, you get a third matrix representing the rotation
that is a composition of the two input rotations. Using a pair of input and output representations, we
define an equivariant function as follows:

!!! definition "Equivariant Function"
    A function $f: \RR^n \rightarrow \RR^m$ is equivariant with respect to representations 
    $\bold{D}_{\textrm{in}}: G \rightarrow \RR^{n \times n}$ and
    $\bold{D}_{\textrm{out}}: G \rightarrow \RR^{m \times m}$ iff 

    $$\bold{D}_{\textrm{out}}\paren{g} \cdot f \paren{\bold{x}} = f\paren{\bold{D}_{\textrm{in}}\paren{g} \cdot \bold{x}}\quad \forall g \in G.$$

This definition subsumes the first two examples above.
In the first example , we had $\bold{D}_\textrm{in}(g) = \bold{R}(g), \bold{D}_{\textrm{out}}(g) = \bold{I}^{1 \times 1}.$
In the second example, we had $\bold{D}_\textrm{in}(g) = \bold{D}_\textrm{out}(g) = \bold{R}(g)$. When $\bold{D}_{\textrm{out}}$ is
the identity matrix, we call the function *invariant*. An important property here
is that equivariance *composes*: that is,

!!! proposition "Composition of Equivariance"
    Suppose $f$ is equivariant w.r.t. input representation $\bold{D}_x$ and output representation $\bold{D}_y$, and
    $g$ is equivariant w.r.t. input representation $\bold{D}_y$ and output representation $\bold{D}_z$. Then $g \circ f$
    is equivariant w.r.t. input representation $\bold{D}_x$ and output representation $\bold{D}_z$, where $\circ$
    denotes function composition.

By ensuring that each layer of a deep neural network is equivariant, the composition 
property guarantees that the *entire network* is an equivariant function
of its input. Typically, the network designer selects the intermediate layer representations to maximize
expressive capability at an acceptable computation cost.

We now have a general definition of equivariance! But what representations should we pick? 
For the chemistry neural networks we consider, we can use
$\bold{R}(g)$ for the 3D input spatial coordinates and $\bold{I}^{1 \times 1}$ for the energy 
defining the network output. We'll need more complicated representations for the intermediate layers,
which we consider in the next section.

## Representations of SO(3) 
How do we build an expressive representation of the rotation group? There's a family
of building block representations we can use: 

$$\bold{D}^{(0)}(g) = \bold{I}^{1 \times 1} \in \RR^{1 \times 1}$$
$$\bold{D}^{(1)}(g) = \bold{R}(g) \in \RR^{3 \times 3}$$ 
$$\bold{D}^{(2)}(g) =\ ...\ \in \RR^{5 \times 5}$$ 
$$...$$
Each $\bold{D}^{(i)}$ matrix is called a **Wigner d-matrix**. One way we can build a new representation 
is by selecting some of these building blocks and arranging them along the diagonal of a new matrix function: 

$$
\bold{D}(g) = 
\begin{bmatrix}
\bold{D}^{(i_1)}(g) & & 0\\
& \ddots & \\
0& & \bold{D}^{(i_D)}(g)
\end{bmatrix}.
$$
How powerful is this method? It turns out that *any representation* of $SO(3)$ is similar to
a Wigner-block diagonal representation: 

!!! theorem "Canonical form for SO(3) Representations"
    Any real representation $\bold{D}(g)$ of $SO(3)$ can be written in the form
    $$
    \bold{D}(g) = \bold{P}^{-1}
    \begin{bmatrix}
    \bold{D}^{(i_1)}(g) & & 0\\
    & \ddots & \\
    0& & \bold{D}^{(i_D)}(g)
    \end{bmatrix}
    \bold{P}
    $$
    for some invertible matrix $\bold{P}$.

Keep this canonical form theorem in mind, because we'll need it in just a bit.
That said, the intermediate representations for our network layers will be Wigner-block diagonal. 
When we write

$$\bold{D}(g) \cong \verb|3x1 + 1x0|,$$

we mean that $\bold{D}(g)$ is Wigner block diagonal with 3 copies of $\bold{D}^{(1)}$ along the diagonal and 1 copy of
$\bold{D}^{(0)}$ along its diagonal. Empirically, picking representations with higher-order Wigner blocks leads
to more accurate, data-efficient neural networks.

Software packages like [`e3nn`](https://e3nn.org/) and [QuTIP](https://qutip.org/) can calculate Wigner d-matrices.
Next, we'll construct functions that are equivariant to these representations. 

## Spherical Harmonic Functions
Much as sines and cosines form a basis for a large class of real-valued scalar functions, the spherical harmonics form
a basis for functions on the sphere $S^2$. The spherical harmonic of degree $\ell$ is a function

$$\bold{Y}^{(\ell)}: S^2 \rightarrow \RR^{2\ell+1}.$$

The main fact we'll need about spherical harmonics relates to equivariance:

!!! theorem "Equivariance Properties of Spherical Harmonics"
    The spherical harmonic of degree $\ell$ is equivariant to output representation $\bold{D}^{(\ell)}$
    and input representation $\bold{D}^{(1)}$:
    $$\bold{D}^{(\ell)}(g) \cdot \bold{Y}^{(\ell)}(\hat r) = \bold{Y}^{(\ell)}\paren{\bold{D}^{(1)}(g) \cdot \hat r}$$

The next ingredient on our roster will allow us to combine two equivariant functions to produce a third. 

## Interacting Equivariant Functions 
Let $\bold{x} \in \RR^n$ and $\bold{y} \in \RR^m$ be two intermediate vectors in some layer of an equivariant network, which
are equivariant functions of the network input $\bold{v}$. We have

$$\bold{D}_x(g) \cdot \bold{x}(\bold{v}) = \bold{x}\paren{\bold{D}_{in}(g) \cdot \bold{v}}$$
$$\bold{D}_y(g) \cdot \bold{y}(\bold{v}) = \bold{y}\paren{\bold{D}_{in}(g) \cdot \bold{v}}$$
Our task is to construct a new vector $\bold{z}$ that, viewed as a function of the input $\bold{v}$,
is equivariant w.r.t. input representation $\bold{D}_{in}$ and some output representation $\bold{D}_z$. 
The [Kronecker Product](https://en.wikipedia.org/wiki/Kronecker_product) offers a general, natural way
to combine the two vectors. We can easily verify

$$(\bold{D}_x \otimes \bold{D}_y)(g) \cdot \br{\bold{x}(\bold{v}) \otimes \bold{y}(\bold{v})} = \bold{x}(\bold{D}_{in}(g) \cdot \bold{v}) \otimes \bold{y}\paren{\bold{D}_{in}(g) \cdot \bold{v}}.$$

Unfortunately, $\bold x \otimes \bold y \in \RR^{nm}$. As vectors flow
through the network, they would grow in length at an intractable rate. A simple fix is dropping
elements of $\bold x \otimes \bold y$, but we can't do this without compromising the equivariance property. 
Furthermore, $\bold{D}_x \otimes \bold{D}_y$ is no longer Wigner block-diagonal.

To solve these two problems, we'll resort to the canonical form theorem from earlier. We first form
$$\bold{z}'(\bold{v}) = \bold{P} \paren{\bold{x}(\bold{v}) \otimes \bold{y}(\bold{v})},$$ 
where $\bold{P}$ is the similarity matrix that block diagonalizes $\bold{D}_x \otimes \bold{D}_y$. If we let $\bold{D}_{z'} = \bold{P} \paren{\bold{D}_x \otimes \bold{D}_y} \bold{P}^{-1}$, note that $\bold{D}_{z'}$ is a block-diagonal representation. We further have 

$$
\begin{equation}
\begin{aligned}
\bold{D}_{z'}(g) \bold{z}'(\bold v)
&= \bold{P} \paren{\bold{D}_x(g) \otimes \bold{D}_y(g)} \bold{P}^{-1} \br{\bold{P} \paren{\bold{x}(\bold v) \otimes \bold{y}(\bold v)}} \\
&= \bold{P} \paren{\bold{D}_x(g) \bold{x}(\bold v) \otimes \bold{D}_y(g) \bold{y}(\bold v)} \\
&= \bold{P} \paren{\bold{x}(\bold{D}_{in}(g) \bold v) \otimes \bold{y}(\bold{D}_{in}(g) \bold v)} \\
&= \bold{z'}(\bold{D}_{in}(g) \bold{v}),
\end{aligned}
\end{equation}
$$

showing that $\bold{z}'$ is an equivariant function of the input. So far, we've solved the second problem
by block diagonalizing the output representation, but not the first issue of length reduction. To do that,
We apply a structured weight matrix $\bold{W}$ to get 

$$\bold z = \bold{WP}\paren{\bold{x} \otimes \bold{y}}.$$

$\bold{W}$ is sparse and accomplishes two objectives: it drops unneeded blocks 
of $\bold{P}\paren{\bold{x} \otimes \bold{y}}$ corresponding to Wigner matrices of high order, 
and it linearly combines the chunks that remain to reduce dimensionality. The weights in $\bold W$
will be learnable parameters of our network.

!figure(images/blog/cg_tensor_product.png, medium, "CG Tensor product and weight matmul.", "The Clebsch-Gordon (CG) tensor product followed by a dimensionality reduction and structured reweighting.")

The operation $\bold{P} \paren{\bold{x} \otimes \bold{y}}$ is called the **Clebsch-Gordon tensor product**.
For convenience, we will often expand this operation to include multiplication by $\bold W$. At this point,
we are ready to assemble our rotation-equivariant neural network! 

## Building a Rotation-Equivariant Graph Neural Network
Let's now turn to the [Nequip](https://github.com/mir-group/nequip) equivariant neural network. Nequip is a 
[graph convolutional network](https://en.wikipedia.org/wiki/Graph_neural_network#Graph_convolutional_network), so the
input atomic coordinates are first processed into a nearest neighbors graph $G = (V, E)$. 
Each node is then assigned a feature vector.

!figure(images/blog/egnn.png, medium, "An equivariant GNN.", "Equivariant graph neural networks combine node features with edge features using the CG tensor product. The resulting vectors are aggregated across the neighborhood of each node.")

At some intermediate layer of the network, let the node features be
$\bold{x_1}...\bold{x_{\abs{V}}}$ with representation $\bold{D}_x$: we will first construct edge 
features $\bold{y_1}...\bold{y_{\abs{E}}}$ using the spherical harmonic functions up to some degree $\ell$ applied to the
unit vector defining the direction of each edge:

$$\bold{y}_{ij} = \textrm{concat}_{i=1}^{\ell}\bold{Y}^{(\ell)}(\hat r_{ij}).$$
The edge vectors are equivariant to representation $\bold{D}_y$. We also need weights 
$\bold{W_1}... \bold{W}_{\abs{E}}$. We will use a standard multilayer perceptron network to
compute these weights from the inter-node distance for each edge.

$$\bold{W}_{ij} = f_{MLP}(\norm{\vec{r}})$$

Observe that $\bold{W}$ is an invariant function of the input coordinates, as
internode distances are rotation-invariant. Finally, we combine the node features with the edge features using
the CG tensor product, aggregating the result for each edge across the node neighborhood. 
Each row $\bold{z_i}$ of the graph convolution output, $i \in \br{\abs{V}}$, is given by

$$\bold{z_i} = \sum_{(i, j) \in \scr N(i)} \bold{W}_{ij} \paren{\bold{x}_j \otimes_{CG} \bold{y}_{ij}}$$
It's easy to check that each row $\bold{z_i}$ is an equivariant function of the network input using
the composition property established above. The resulting node vectors may be further processed
by linear neural network layers or normalization.

The graph convolution, illustrated in the figure above, repeats over multiple layers. The final layer produces a collection
of scalars for each node, which are summed and reduced to get the final node energy output. Backpropagating through the
network with respect to the atomic positions $\bold{R}$ yields the atomic forces. With a little more math, we can make
these networks reflection-equivariant as well. A network that is equivariant to 
the Euclidean distance-preserving transforms of rotation, translation, and reflection is *E(3)-equivariant*.

As in most equivariant chemical foundation models, the computational bottleneck in Nequip is the calculation of CG tensor
products for each edge. Due to high sparsity of the Clebsch-Gordon coefficient tensor, the irregular workload is 
anathema to GPUs that are optimized for low-precision dense matrix multiplication. 

## OpenEquivariance: Turbocharging CG Tensor Products
*OpenEquivariance* is our attempt to accelerate the CG tensor product; I've sketched out the package
architecture below. [Our 2025 paper](https://epubs.siam.org/doi/10.1137/1.9781611979084.3) details many 
of the GPU kernel optimizations we made to achieve high performance, but does not cover the software stack we
used. That's what this section covers, and getting this architecture correct was a critical stepping stone to
ensuring wide adoption of our package. 

!figure(images/blog/oeq_software_stack.svg, large, "OpenEquivariance software stack.", "The OpenEquivariance software stack.")

Because tensor product operations vary wildly between network architectures (and indeed, even between layers of 
the same network!), OpenEquivariance uses JIT compilation to achieve high performance. Users begin by
specifying the input and output representations (as well as the structure of the weight 
matrix $\bold W$) with standard `e3nn` syntax. 
OpenEquivariance uses [Jinja](https://jinja.palletsprojects.com/en/stable/) templates to generate a kernel
that minimizes DRAM-SRAM traffic, then uses a C++ adapter to compile the kernels through either
the NVIDIA runtime compiler (NVRTC) or HIP runtime compiler (HIPRTC).

The compiled kernels are hashed and cached until a user running either PyTorch or JAX executes 
the tensor product. Binding codes for either framework retrieve the cached kernel binaries and dispatch 
them to the hardware. We considered a variety of other package designs, but as this table shows, each
has a specific drawback.

| Approach            | Cross-GPU? | Cross-ML-Framework? | `torch.compile()`? | Notes                                                                            |
|---------------------|------------|---------------------|--------------------|----------------------------------------------------------------------------------|
| Precompiled Kernels | ✅          | ✅                   | ✅                  | Too much case handling / branching within a kernel compared to JIT.              |
| CUDA Python         | ⛔️          | ✅                   | ⛔️                  | Offers streamlined JIT compiler and CUDA API access, not much else.              |
| Triton              | 🤔          | ⛔️                   | ✅                  | Easy to program, but sacrifices too much SRAM control.                           |
| OpenEquivariance    | ✅          | ✅                   | ✅                  | Requires high upfront development cost for JIT compiler / ML framework bindings. |

Users of chemical foundation models need to call their model from C++, e.g. when integrating with LAMMPS; this rules
out CUDA Python. Triton has relatively poor performance for this kernel, ceding too much control to the automatic shared
memory manager. Unfortunately, building a sufficiently-general kernel generator required us to hand-roll much of our
C++ infrastructure. 

Today, OpenEquivariance is integrated with [Nequip](https://github.com/mir-group/nequip), 
[MACE](https://github.com/acesuit/mace), [Sevennet](https://sevennet.readthedocs.io/en/latest/),
and [Nequix](https://github.com/atomicarchitects/nequix/commits/main/). In future posts, I'll cover 
further details about our package and lessons learned building it.

