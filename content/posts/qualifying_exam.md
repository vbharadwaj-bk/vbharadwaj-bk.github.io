---
Title: My Qualifying Exam 
Date: 2024-01-17 
Category: computer-science 
Summary: A landing page for my qual at Berkeley. 
thumbnail: "images/blog/qual_splash_img.png"
---
I will take my PhD qualifying exam on January 17, 2024.
The exam consists of a presentation of my research so far
and plans for future work. On this page, you can read a bit
more about the research that I'll be presenting. 

The presentation covers the following work (see
[my list of publications ]({filename}/pages/publications.md) if you want more information):

1. [Fast Exact Leverage Score Sampling from Khatri-Rao Products with Applications to Tensor Decomposition](https://arxiv.org/abs/2301.12584). This paper (which appeared at
NeurIPS 2023) explains how to draw samples according to the
*leverage score distribution* of a column-wise Kronecker
product of several matrices efficiently. We apply this
method to efficiently decompose massive sparse tensors.

2. [Distributed-Memory Randomized Algorithms for Sparse CP Decomposition](https://arxiv.org/abs/2210.05105). We
extend the methods from the first paper to the
distributed-memory parallel setting and optimize them
to avoid processor-to-processor communication. We decompose
the Reddit tensor with around 4.7 billion nonzeros in under
two minutes on four Perlmutter CPU nodes! 

3. [Distributed-Memory Sparse Kernels for Machine Learning](https://arxiv.org/abs/2203.07673). The methods above deal
with tensor decomposition / factorization. This work
deals instead with sparse matrix *completion*, 
a related problem where only a subset of entries 
are observed. We recast the factorization problem 
to use the Sampled-Dense-Dense Matrix Multiplication
(SDDMM) kernel and Sparse-Times-Dense Matrix Multiplication
(SpMM) kernel and develop dual communication-avoiding
formulations for both.
