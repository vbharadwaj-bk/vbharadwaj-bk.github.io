---
Title: Writing C++ Extensions for Numpy code 
Date: 2024-04-04 
Category: computer-science 
thumbnail: 
Summary: >
  A tutorial on writing C++ extensions for Python using Pybind11
  that interface seamlessly with Numpy or Scipy. 

latex_macro_file: 'content/latex/common_macros.yaml'
---
There are a lot of times when I've started coding a project in Python, 
only to hit a runtime bottleneck for some fundamental operation I need
in an algorithm. Python is fantastic for fast prototyping and 
even production-ready machine learning, but performance really suffers if
your project needs primitives that aren't exposed by libraries like
Numpy, Scipy, or Pytorch. This is a tutorial on extending Python
by writing C++ extensions using Pybind11. No complicated buildfiles
required! We'll be using Ben Thompson's awesome [cppimport](https://github.com/tbenthompson/cppimport)
extension, which you can install via `pip`. 

There are many other tutorials on Pybind11 online. This tutorial focuses
specifically on interacting with Numpy / Scipy code. Does either of the following apply to you?

1. You're writing an app mostly in Scipy / Numpy, but there's one part of your
algorithm that doesn't map neatly onto the functions that these libraries provide.
2. You have a large existing C++ codebase or library, and you want a set of Python bindings
that enable users to call into these libraries. 

If so, you're in the right place. 

### Our Example Application: Breadth-First Search on a Graph 
Let's say we want to perform breadth-first search (BFS) on a graph $G=(V, E)$ efficiently. For this tutorial, 
we're going to use the Matrix-Market (.mtx) format of `bcspwr02`, a small power system graph that
you can [download from the Suitesparse Matrix Collection](https://sparse.tamu.edu/HB/bcspwr02).
Scipy contains a blazingly-fast multithreaded routine to load the adjacency matrix $A$ of the graph: 

```python
import scipy as sp

path = '/Users/Vivek/Desktop/bcspwr02.mtx'

adjacency = None
with open(path, 'rb') as f:
    adjacency = sp.io.mmread(f).tocsr()
```
After executing this code, `adjacency` is a compressed-sparse-row (CSR) Scipy sparse matrix 
containing the graph adjacency matrix (Wikipedia has a [nice explanation](https://en.wikipedia.org/wiki/Sparse_matrix#Compressed_sparse_row_(CSR,_CRS_or_Yale_format)) of the format). There are three fields
of the `adjacency` class that we care about, and for this tutorial, the only relevant pieces of information
are their datatypes and sizes. I've also listed their semantic meaning below, in case you're interested, but 
feel free to ignore that info. 

1. `adjacency.data`: A 1D Numpy array of type `float64` with length $\textrm{nnz}(A)$. The value 
`adjacency.data[i]` gives the weight of nonzero $i$ from $A$, where the nonzeros are ordered 
first by row index, then by column index.

2. `adjacency.indices`: A 1D Numpy array of type `int32` with length $\textrm{nnz}(A)$. The value 
`adjacency.indices[i]` gives the column index of nonzero $i$ from $A$.

3. `adjacency.indptr`: A 1D numpy array of type `int32` with length 
$\E{V}$. The value
