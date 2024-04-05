---
Title: Writing C++ Extensions for Numpy code 
Date: 2024-04-04 
Category: computer-science 
thumbnail: 
Summary: >
  A tutorial on writing C++ extensions for Python using Pybind11
  that interface seamlessly with Numpy or Scipy. 

toc: 
  sidebar: True
latex_macro_file: 'content/latex/common_macros.yaml'
---

### Introduction
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

If so, you're in the right place. This tutorial will show you how to
shuttle large amounts of data back and forth between the Python and
C++ layers of your code.

### Example Application: BFS on a Graph 
Let's say we want to write a breadth-first search (BFS) routine for a 
graph $G=(V, E)$. For this tutorial, 
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
$\abs{V}+1$. The nonzeros in the range
`adjacency.indptr[i]` (inclusive) to `adjacency.indptr[i+1]` (exclusive)
all belong to row $A_{i:}$.

You could probably write a BFS implementation with just a few lines
of code in Python, but this would be exceptionally slow for graphs
with billions of edges. Our goal is to write a C++ extension that
performs the search efficiently. 

### Installing and Getting Started with cppimport 
The [cppimport](https://github.com/tbenthompson/cppimport) package is
by far the simplest (and coolest) way I've seen to start writing
C++ extensions quickly. To get started, install the package via 
`pip install pybind11`. Open an editor and create a file 
file `bfs_extension.cpp`:

```C++ 
//cppimport
/* extension.cpp */
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <iostream>

using namespace std;
namespace py = pybind11;

void hello_world() {
    cout << "Hello world!" << endl;
}

PYBIND11_MODULE(bfs_extension, m) {
    m.def("hello_world", &hello_world);
}
/*
<%
setup_pybind11(cfg)
%>
*/
```
That's all you need to create a working extension! Let's walk through
the key lines:

1. `//cppimport`: This first-line comment is needed if you're using
cppimport to compile your extensions.

2. `#include<pybind11/pybind11.h>`: This header (along with the Numpy
header below it) exposes classes and functions necessary to interface
with Python.

3. `PYBIND11_MODULE...`: After declaring a dummy test function
`hello_world`, we define a Python module named `bfs_extension` and
give it a local name `m`. We expose the function to the Python
layer with the `m.def` statement on the next line. Note that the names
for the function at the Python and C++ layers **do not** have to be
the same. For example, you can rename the `hello_world` function
at the C++ layer by providing a different string argument in the 
`m.def` line, which can be very useful.

4. `setup_pybind11(cfg)`: More boilerplate related to cppimport; we'll
cover this in a little bit, but you can ignore this set of comments for now.

!!! tip "Tip: Using an Alternate Build System"
    You don't have to use cppimport to compile your extension, and it's
    probably not the best choice for large, complex builds. 
    The extension `.cpp` file can be compiled via CMake or any other
    build system of your choice, provided that you supply the Pybind11 
    header paths and libraries. 
    
Let's try calling our extension from Python. Before you try your extension, 
make sure that you export the shell variables `CC` and `CXX` to the
C / C++ compilers of your choice, or else `cppimport` will attempt
to locate compilers for you. Fire up a terminal in the same folder
as your extension file and enter the following: 

```bash
shell ~ % python
Python 3.11.8 | packaged by conda-forge | (main, Feb 16 2024, 20:49:36) [Clang 16.0.6 ] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import bfs_extension
>>> bfs_extension.hello_world()
Hello, world!
>>>
```
If all goes well, you should see `Hello, world!` printed on your terminal
prompt. Congratulations! You have a working extension.

### Interfacing with Numpy


