---
Title: Writing C++ Extensions for Numpy Code 
Date: 2024-04-04 
Category: computer-science 
thumbnail: 
Summary: >
  A tutorial on writing C++ extensions for Python using Pybind11
  that interface seamlessly with Numpy or Scipy. 

latex_macro_file: 'content/latex/common_macros.yaml'
toc:
  sidebar: True

latex_macros:
  abs: '["\left| #1 \right|", 1]'
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
specifically on interacting with Numpy / Scipy code. Does any of the following apply to you?

1. You're writing an app mostly in Scipy / Numpy, but there's one part of your
algorithm that doesn't map neatly onto the functions that these libraries provide.
2. You have a large existing C++ codebase or library, and you want a set of Python bindings
that enable users to call into these libraries. 
3. Your application requires shared-memory multithreading,
which Python does not (at the time of writing) support. 

If so, you're in the right place. Before we start, I should mention that this
tutorial is based on the following resources. 

1. The official [Pybind11 documentation](https://pybind11.readthedocs.io/en/stable/index.html), and in particular the [page on Numpy arrays](https://pybind11.readthedocs.io/en/stable/advanced/pycpp/numpy.html?highlight=Eigen#numpy).

2. The [README documentation for the cppimport extension](https://github.com/tbenthompson/cppimport/tree/main).

The Pybind11 documentation has a comprehensive set of example codes 
with better coding practices than what this tutorial exposes. That said,
I hope that this tutorial lowers the barrier to entry to create extensions
and saves you some Googling. 

### Getting Started 
You can download the finished code for this tutorial at [this git repo](). This
tutorial has been tested on Mac (Apple Silicon) and Linux systems. If you're 
using Windows, try [Windows Subsystem for Linux](https://learn.microsoft.com/en-us/windows/wsl/about).

Fire up a terminal / text-editor and create 
a directory `Pybind11_tutorial`. Inside, create a pair of files `my_extension.cpp`
and `calling_code.py`. Your directory structure should look like this:

```console
Pybind11_tutorial (directory)
├── calling_code.py
└── my_extension.cpp
```

We will do all of our work inside the `Pybind11_tutorial` directory. 
The [cppimport](https://github.com/tbenthompson/cppimport) package is
by far the simplest (and coolest) way I've seen to start writing
C++ extensions quickly. Install the package via

```pip install cppimport``` 

Then enter the following into `my_extension.cpp`:

```C++ 
//cppimport
/* my_extension.cpp */
#include <pybind11/pybind11.h>
#include <iostream>

void hello_world(int x) {
    std::cout << "Hello world! Your number is " << x << std::endl;
}

void print_double(double x) {
    std::cout << "The double you entered is " << x << std::endl;
}

PYBIND11_MODULE(my_extension, m) {
    m.def("hello_world", &hello_world)
    m.def("print_double", &print_double);
}
/*
<%
setup_pybind11(cfg)
%>
*/
```
That's all you need to create a working extension! Let's walk through
the key lines:

1. `//cppimport`: This first-line comment is **necessary** if you're using
cppimport to compile your extensions.

2. `#include<pybind11/pybind11.h>`: This header exposes 
classes and functions necessary to interface with Python.

3. `PYBIND11_MODULE...`: After declaring two test functions
`hello_world` and `print_double`, we define a Python module named 
`my_extension` and give it a local name `m`. We expose twofunction to the Python
layer with the `m.def` statements on the next two lines. Note: the function
names at the Python and C++ layers **do not** have to be
the same. For example, you can rename the `hello_world` function
at the C++ layer by providing a different string argument in the 
`m.def` line, which can be very useful.

4. `setup_pybind11(cfg)`: More boilerplate related to 
cppimport. This is a Mako block; we'll cover what you can do with
this in a little bit, but you can ignore this set 
of comments for now.

!!! tip "Tip: Using an Alternate Build System"
    You don't have to use cppimport to compile your extension, and it's
    probably not the best choice for large, complex builds. 
    The extension `.cpp` file can be compiled via CMake or any other
    build system of your choice, provided that you supply the Pybind11 
    header paths and libraries. 
    
Now let's write the corresponding code to call the extension at the Python layer. 
Enter the following into
`calling_code.py`:

```python
# calling_code.py
import cppimport 
import cppimport.import_hook
import my_extension 
my_extension.hello_world(5)
my_extension.print_double(3.14)
```

Let's test it out. Before you run the code, 
make sure that you export the shell variables `CC` and `CXX` to the
C / C++ compilers of your choice, or else `cppimport` will attempt
to locate compilers for you. Fire up a terminal and try the following:
```console
[shell]% python calling_code.py
Hello world! Your number is 5
The double you entered is 3.14
```
You should see the output listed above on 
your console. Congratulations! You now have a working extension. 

### Behind the Scenes 
Here's a little more information about what's going on.
When you use `import cppimport.import_hook`, you're enabling 
cppimport to compile extensions from `.cpp` files as needed. 
When the line `import my_extension` executes, cppimport
notices that you have a `.cpp` file in the current directory
with the same name as the module and the comment `//cppimport`
as the first line. The cppimport package then compiles the 
Python module, and you can subsequently call any of the
methods defined. 

!!! tip "Tip: Move Extension Files to a Separate Folder"
    If you want to keep your codebase clean, try moving
    the `.cpp` extension files to a subfolder of your main
    directory. If `my_extension.cpp` is located in folder
    `cpp_ext` relative to the current directory, the line
    `import cpp_ext.my_extension` will allow you to use
    the extension correctly. 

One smart feature about cppimport is that the extension is
*only recompiled when a C++ dependency file changes*. Later
in this tutorial, we'll mention how to specify the list of
dependencies explicilty for multi-file builds. For now,
try executing the Python code a second time. You'll notice
that the second execution is marginally faster, since cppimport
doesn't bother recompiling the unchanged extension file. 

### Passing Arguments to C++ 
Variables of many common datatypes can be seamlessly passed 
between the C++ and Python layers . Here's an example
of a function defined at the C++ layer that works exactly
as you expect when called from Python.
```C++
...
uint64_t greet_and_return5(std::string name) {
    std::cout << "Howdy, " << name << std::endl;
    return 5;
}
...
```
This magic is brought to you by Pybind11. That said, passing
scalar arguments back and forth isn't that interesting. Usually,
we want to make *arrays of data* from the Python layer accessible
to C++, or vice-versa. Let's say we want to write a C++ extension 
to compute the Frobenius norm of a matrix 
$X \in \RR^{n \times m}$, defined as

$$\norm{X}_F = \sum_{i=1, j=1}^{n, m} X_{ij}^2$$

Here's what the calling code looks like at the Python layer:
```python
import numpy as np
import cppimport, cppimport.import_hook
import my_extension

X = np.random.normal(size=(500, 5), dtype=np.float64)
f_norm = my_extension.f_norm(X)
```
Here's what that extension looks like at the C++ layer:

```C++ 
//cppimport
/* my_extension.cpp */
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cmath>

using namespace std;
namespace py=pybind11;

double f_norm(py::array_t<double> mat_py) {
    py::buffer_info info = mat_py.request();
    double* ptr = static_cast<double*>(info.ptr);
    uint64_t num_elements = info.shape[0] * info.shape[1];

    double sq_fnorm = 0.0;
    for(uint64_t i = 0; i < num_elements; i++) {
        sq_fnorm += ptr[i];
    }
    return sqrt(sq_fnorm);
}

PYBIND11_MODULE(my_extension, m) {
    m.def("f_norm", &f_norm);
}
/*
<%
setup_pybind11(cfg)
%>
*/
```
Neat! Let's step through the code.

1. We define an argument to the function `f_norm` of type
`py::array_t<double>`, corresponding to the Numpy datatype 
`np.float64`.
2. The class `py::buffer_info` captures all relevant information
about the Python buffer passed in. We extract the pointer to
the data (which is stored in row-major format) as well as the
shape.
3. We iterate through the input matrix (accessing it through
the raw data pointer) to compute the squared Frobenius norm,
and return it as a scalar value.

Two additional points: first, none of the data in the input
array `X` is copied. The C++ layer just gains access to a 
pointer for the head of the memory chunk allocated for the
data. Second, the class `py::array_t` offers a convenient 
`[]` operator to access the contents of the array, which the
example above does not use. I personally find it comfortable
to work with the raw data pointer, since I'm not sure what 
kind of overhead the `[]` operator incurs. Libraries like
BLAS / LAPACK implementations also typically require raw
pointer inputs, so it's useful to know how to extract them
from the Python buffers.

### Mutating and Returning Data from C++ 
We can also mutate data in Python buffers directly.
Suppose we want to add to add 3 to all elements of a
matrix `X`:
```python
import numpy as np
import cppimport, cppimport.import_hook
import my_extension

X = np.random.normal(size=(500, 5), dtype=np.float64)
my_extension.add3(X)
```
Here's the extension to do that:

```C++ 
//cppimport
/* my_extension.cpp */
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cmath>

using namespace std;
namespace py=pybind11;

void add3(py::array_t<double> mat_py) {
    py::buffer_info info = mat_py.request();
    double* ptr = static_cast<double*>(info.ptr);
    uint64_t num_elements = info.shape[0] * info.shape[1];

    for(uint64_t i = 0; i < num_elements; i++) {
        ptr[i] += 3.0;
    }
}

PYBIND11_MODULE(my_extension, m) {
    m.def("add3", &add3);
}
/*
<%
setup_pybind11(cfg)
%>
*/
```

!!! danger "Danger: Auto-conversions create unexpected behavior" 
    Suppose your Python extension takes an argument of type
    `py::array_t<double>`, but you pass a Numpy array of 
    type `np.float32`. This actually works fine: Pybind11
    will automatically convert the single-precision float
    array to a double precision array (incurring some overhead
    in the process). But if you attempt
    to MUTATE values at the C++ layer, these changes will
    not reflect in the original array. Auto-conversion can
    be disabled in Pybind11.

Finally, you can also initialize and return Numpy arrays from the C++
layer; here's an revsision of the `add3` function that returns a new buffer
instead of mutating in place:

```C++ 
//cppimport
/* my_extension.cpp */
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cmath>

using namespace std;
namespace py=pybind11;

/*
 * Returns a copy
 */
void add3_returncopy(py::array_t<double> mat_py) {
    py::buffer_info info_in = mat_py.request();
    double* ptr_in = static_cast<double*>(info_in.ptr);
    uint64_t num_elements = info.shape[0] * info.shape[1];

    auto result = py::array_t<double>(info_in.size);
    py::buffer_info info_out = result.request();
    double* ptr_out = static_cast<double*>(info_out.ptr);

    for(int i = 0; i < num_elements; i++) {
        ptr_out[i] = ptr_in[i] + 3.0;
    }
}

PYBIND11_MODULE(my_extension, m) {
    m.def("add3_returncopy", &add3);
}
```


### Customizing the cppimport Build Process 
What happens if you want to link an external library to
your extension or specify additional flags to the C++
compiler / linker? This is no problem if you 
build your extension with CMake: you can
use `target_include_directories`, 
`target_link_libraries`, and `target_compile_options`.



### Example Application: BFS on a Graph 
Let's say we want to write a breadth-first search (BFS) routine for a 
graph $G=(V, E)$. For this tutorial, 
we're going to use the Matrix-Market (.mtx) format of `bcspwr02`, a small power system graph that
you can [download from the Suitesparse Matrix Collection](https://sparse.tamu.edu/HB/bcspwr02).
Scipy contains a blazingly-fast multithreaded routine to load the adjacency matrix $A$ of the graph: 

```python
import numpy as np
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
