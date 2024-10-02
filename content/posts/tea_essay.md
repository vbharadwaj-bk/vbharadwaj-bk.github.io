---
Title: "Cookie Cutters: Scaling a Parallel Computing Class"
Date: 2024-05-17
Category: computer-science 
Summary: |
  An essay I wrote for the 2023-2024 Teaching
  Effectiveness Award contest. This essay
  was one of 15 submissions chosen for the award. 
thumbnail: "images/blog/cookies.jpeg" 
---

**Background**: 
*The Berkeley Teaching Effectiveness Award (TEA)
recognizes around 15 graduate
student instructors each year who have identified and 
fixed a particular problem in their classes. 
Winners are selected on the basis of an essay
they submit.
This essay won the [2023-2024 award](https://gsi.berkeley.edu/programs-services/award-programs/teaching-effectiveness/tea-recipients/tea-year/tea-2020-2025/), and a 
[copy of this essay](https://gsi.berkeley.edu/cookie-cutters-scaling-a-parallel-computing-class-while-retaining-its-humanity/) was posted to the GSI resource center
website. Also check out
my [student reviews for CS267 in 2022]({static}/pdf/teaching_reviews/reviews_berkeley.pdf)!* 


!TEMPLATE!
<div class="row">
    <div class="col-2">
    </div>
        <div class="col-8 card border-0 bg-white p-1 mb-3">
        {{ figure(path="images/blog/cookies.jpeg",title="A tray of cookies.", class="img-fluid rounded z-depth-1", zoomable=False) }}
        <div class="caption">
        A delicious tray of cookies. Wikimedia
        Commons public domain.
        </div>
</div>
<div class="col-2">
</div>
</div>
!TEMPLATE!


The demand for computer science classes has 
ballooned across the nation, and UC Berkeley 
is no exception. Given massive class sizes 
of hundreds of students, the workload 
for teaching assistants (TAs) is so immense 
that department union members 
voluntarily requested *pay cuts* last year 
in exchange for increases in staffing. 
Is computer science doomed to become 
“Education, Inc.”, with all student 
interactions kept to a minimum as we 
stamp out degrees?

I don’t think so, provided we pay attention to 
an overlooked part of teaching: logistics. 
In 2022, I was one of just four TAs for 
CS267: Applications of Parallel Computers, 
which began with over 200 students. 
CS267 teaches students how to program 
the most powerful scientific computers on 
the planet, including the massive 
Perlmutter supercomputer at Lawrence 
Berkeley Lab. The class size was at least 
30% larger than prior iterations. How were 
we going to cope with the huge influx 
of students while ensuring that 
everyone received support? I used two 
major tactics: a relentless focus on 
automating the logistics of the class to 
free up my time, which I then spent lavishly 
on student office hours and 
personalized support. 

TA logistics is not inspirational or rewarding 
work, but it makes a world of difference to 
students and their harried professors. Before 
every assignment, I mentally worked through the 
information the students needed to submit to the 
instructors to use our computer systems (e.g. account 
usernames, teammate identities, graduate / undergraduate status, etc.). 
Every three weeks, the students would receive a 
short Google survey requesting this information, which 
often changed between assignments. I then wrote 
custom scripts to automatically lift the survey 
results, form groups on bCourses, and submit new 
computer account requests. To return project 
proposal feedback to the students, I wrote a 
bot that sent hundreds of individual emails with 
our personalized feedback directly to each student; 
in years prior, we sent those emails manually. To 
set up the final project poster session, I built 
a program to automatically generate a presentation 
schedule based on which TAs / professors gave 
feedback for their initial project proposals. This 
ensured continuity of instruction and feedback, with 
the same instructors tracking a project from inception 
to completion. I even rewrote our autograder (which 
had slowed to a crawl due to the large class size) to 
grade several assignments in parallel, allowing us 
to return feedback to students much more quickly. 
The cumulative impact of these small actions was 
**greater than the sum of its parts**, freeing 
both instructors and students to focus on the class content itself.

In short, I tried to automate away every piece of 
repetitive work taking time away from my real job: 
teaching. With my extra time, I ran two blocks 
of office hours each week which dozens of students 
attended regularly. I tripled the amount of 
recitation content for the first homework assignment from 
the prior year, covering a wide array of optimizations 
that students could use in their homework. I racked 
up more than 800 contributions on Piazza as I 
responded to almost every question online. In my 
course surveys at the end of the year, 16 students 
praised the logistical handling, Piazza support, and 
office hours as course highlights that helped them 
succeed, with one student comparing our (graduate) 
class favorably to pedagogy-focused undergraduate 
courses. Using “cookie cutters” and other tools to 
automate tasks doesn’t make teaching impersonal. 
In fact, it’s the only way we can satiate today’s hunger 
for a computer science education. It makes time for us 
to focus on our recipe for teaching and for 
meaningful, one-on-one interactions with students 
- the sweetest and most gratifying parts of our work.


