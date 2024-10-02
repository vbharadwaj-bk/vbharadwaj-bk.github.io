---
Title: A Math + CS Double-Major Schedule at Caltech
Date: 2023-11-24 
Category: personal 
thumbnail: "images/blog/schedule_thumbnail.png"
Summary: >
  A table of courses that I took as an undergraduate, 
  useful for anyone else who might be
  considering a double major. 
---
I thoroughly enjoyed my time at Caltech taking classes.
In retrospect, I wish I had spent a bit more time 
doing research, but I regret nothing. You can 
find my undergraduate class schedule below. 

!TEMPLATE!
{% set advanced_placement =
    [
        ("Ma1A", "Calculus of One and Several Variables & Linear Algebra"),
        ("Ma1C", "Calculus of One and Several Variables & Linear Algebra (Multivariable)"),
        ("Ph1A", "Classical Mechanics and Electromagnetism") 
    ]
%}

{% set schedule = [
    [
        ("Fall 2016", [
            ("CS1", "Intro. to Computer Programming"),
            ("CS9", "Intro. to Computer Science Research (Pizza Class)"),
            ("Ch1A", "General Chemistry"),
            ("En25", "The Rhetoric of Superiority"),
            ("Ma2", "Differential Equations"),
            ("Ma6A", "Intro. to Discrete Mathematics"),
        ]),
        ("Winter 2017", [
            ("CS2", "Intro. to Programming Methods"),
            ("CS21", "Decidability and Tractability"),
            ("Ch1B", "General Chemistry"),
            ("Ph11B", "Freshman Seminar: Research Tutorial"),
            ("Ma1B", "Calculus of One and Several Variables and Linear Algebra"),
        ]),
        ("Spring 2017", [
            ("Bi1", "Principles of Biology"),
            ("CS38", "Intro. to Algorithms"),
            ("Ge1", "Earth and Environment"),
            ("H2", "Baseball and American Culture, 1840 to the Present"),
            ("Ph1C", "Classical Mechanics & Electromagnetism")
        ]),
    ],
    [
        ("Fall 2017", [
            ("CS11", "Computer Language Lab"),
            ("CS121", "Relational Databases"),
            ("CS177A", "Discrete Differential Geometry: Theory & Applications"),
            ("CS156A", "Learning Systems"),
            ("Ma5A", "Intro. to Abstract Algebra"),
            ("PS12", "Intro. to Political Science"),
        ]),
        ("Winter 2018", [
            ("CS155", "Machine Learning / Data Mining"),
            ("CS4", "Fundamentals of Computer Programming"),
            ("Ec11", "Intro. to Economics"),
            ("Ma5B", "Intro. to Abstract Algebra"),
            ("Ph2B", "Waves, Quantum Mechanics, and Statistical Physics"),
        ]),
        ("Spring 2018", [
            ("CS24", "Intro. to Computing Systems"),
            ("CS153", "Current Topics in Theoretical Computer Science (Communication Complexity)"),
            ("CS156B", "Learning Systems"),
            ("L103C", "Intermediate French"),
            ("Ma5C", "Intro. to Abstract Algebra"),
        ]),
    ],
    [
        ("Fall 2018", [
            ("CS11", "Computer Language Lab: ACM-ICPC"),
            ("CS80A", "Undergraduate Thesis"),
            ("CS150", "Probability & Algorithms"),
            ("En102", "Origins of Science Fiction"),
            ("Ma108A", "Classical Analysis"),
            ("Ma177A", "Computability Theory"),
        ]),
        ("Winter 2019", [
            ("ACM216", "Markov Chains, Discrete Stochastic Processes and Applications"),
            ("CS90", "Undergraduate Reading in Computer Science"),
            ("Ch3X", "Experimental Methods in Solar Energy Conversion"),
            ("Ec112", "Bayesian Statistics"),
            ("Ma177B", "Computability Theory"),
            ("PE6", "Core Training, Beginning/Intermediate")
        ]),
        ("Spring 2019", [
            ("CS90", "Undergraduate Reading in Computer Science"),
            ("CS115", "Functional Programming"),
            ("CS151", "Complexity Theory"),
            ("En89", "Writing the News - Journalistic Writing"),
            ("Ma108C", "Classical Analysis"),
        ]),
    ],
    [
        ("Fall 2019", [
            ("APh9A", "Solid-State Electronics for Integrated Circuits"),
            ("CS90", "Undergraduate Reading in Computer Science"),
            ("EE126A", "Information Theory"),
            ("Ec105", "Firms, Competition, and Industrial Organization"),
            ("Ma10", "Oral Presentation"),
            ("Ma109A", "Intro. to Geometry and Topology"),
        ]),
        ("Winter 2020", [
            ("EE10A", "Intro. to Digital Logic and Embedded Circuits"),
            ("En86", "Fiction and Creative Nonfiction Writing"),
            ("En117", "Picturing the Universe"),
            ("Ma109B", "Intro. to Geometry and Topology"),
            ("Ma140", "Probability"),
            ("PE10", "Aerobic Dance")
        ]),
        ("Spring 2020", [
            ("H134", "Birds, Evolution, Speciation and Society"),
            ("Ma109C", "Intro. to Geometry and Topology"),
            ("Ma6C", "Intro. to Discrete Mathematics"),
            ("Ph2C", "Waves, Quantum Mechanics, and Statistical Physics"),
            ("SEC11", "Written Academic Communication in Engineering and Applied Science"),
            ("VC72", "Data, Algorithms, and Society")
        ]),
    ]
] 
%}

<div class="row">
    <div class="col-md-12 p-2">
        <div class="card">
        <div class="card-body">
        <h5 class="card-title">Advanced Placement</h5>
            <table class="table mb-0">
                {% for course in advanced_placement %}
                <tr>
                    <td><b>{{ course[0]}}</b>&nbsp;&nbsp;&nbsp;<div style="font-size:13px">{{ course[1] }}</div></td>
                </tr>
                {%- endfor -%}
            </table>
        </div>
        </div>
    </div>
</div>

{%- for year in schedule -%}
<div class="row">
    {%- for term in year -%}
    <div class="col-sm-12 col-md-4 d-md-flex p-2 align-items-stretch">
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



