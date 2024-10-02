---
Title: My Graduate Course Schedule
Date: 2024-04-06 
Category: personal 
thumbnail: "images/blog/soda_thumbnail.jpeg"
Summary: >
  A page listing my coursework at UC Berkeley.
---
As of 2024, EECS PhD students at UC Berkeley need to complete
24 units of coursework consisting of:

- 12 units of major classes
- 6 units of minor classes
- 6 units of elective classes

My CSGF fellowship also mandated that I take 2 classes
in computer science, 2 classes in mathematics, and
2 elective classes, all of which I overlapped
with my Berkeley coursework. Below, you can find the
schedule I used to satisfy these requirements. Not listed
below: a COMPSCI 375 teaching class I took on teaching
techniques in computer science. 

By far, my favorite classes were COMPSCI 267 and
MATH 221 (taught by my advisers). There's
some obvious bias on my part, but these
courses also happen to provide 
highly-organized and polished experiences
to students.


!TEMPLATE!
{% set schedule = [
    [
        ("Fall 2020", [
            ("COMPSCI 281A", "Statistical Learning Theory"),
            ("MATH 221", "Advanced Matrix Computations")
        ]),
        ("Spring 2021", [
            ("COMPSCI 267", "Applications of Parallel Computers"),
            ("COMPSCI 270", "Combinatorial Algorithms and Data Structures")
        ])
    ],
    [
        ("Fall 2021", [
            ("PHYSICS 288", "Bayesian Data Analysis and ML for Physical Sciences"),
            ("COMPSCI 262A", "Advanced Topics in Computer Systems")
        ]),
        ("Spring 2022", [
            ("BIOENG 241", "Probabilistic Modeling in Computational Biology"),
            ("ELENG C227C", "Convex Optimization and Approximation")
        ]),
    ]
] 
%}

{%- for year in schedule -%}
<div class="row">
    {%- for term in year -%}
    <div class="col-sm-12 col-md-6 d-md-flex-row p-2 align-items-stretch">
        <div class="card">
        <div class="card-body">
            <h5 class="card-title">{{ term[0] }}</h5>
            <table class="table mb-0">
                {% for course in term[1] %}
                <tr>
                    <td><b>{{ course[0]}}</b>&nbsp;&nbsp;&nbsp;<div style="font-size:13px">{{ course[1] }}</div></td>
                </tr>
                {%- endfor -%}
            </table>
        </div>
        </div>
    </div>
    {%- endfor -%}
</div>
{% endfor %}

!TEMPLATE!