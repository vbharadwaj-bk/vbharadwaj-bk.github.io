---
Title: A Microblog of Recent Events 
Date: 2026-10-21 
Category: personal 
thumbnail_icon: '<i class="fa-solid fa-book fa-5x"></i>'
Summary: >
  Journaling some observations. 
  
---

## October 21, 2027
I read my new lease agreement, then fed it to Claude to flag any issues. It highlighted a
page that I wasn't aware of at first and is very good at querying information. For example:
without digging through dozens of pages, I could just ask it what internet providers the
leasing company offers. 

Claude always seems to find an "red flag" or nitpick, though. This time, it fixated on the
year of the last lead report (2006), which I found to be a minor issue. LLMs do this for
code reviews too, which is why I find it pretty much useless for that purpose. Every
"possibly None" variable becomes a P1 fire. The same issue shows up in Claude-generated test
suites: many of the tests cover tautologies or corner cases that could never arise in practice.
Worse yet, bloated test increase iteration time when developing and lull you into a false sense
of security. 

I've concluded that a code review doesn't *have* to catch every single issue for prototype code.
For production systems, a consistent style guide or library of best-practice idioms could be 
automatically enforced by an LLM. A code review should cover high-level logical changes, while
tests should exercise nontrivial parts of the code. 


## October 16, 2027
There is upheaval in mathematics right now due to a 
[mechanized onslaught of proofs](https://github.com/openai/math) brought by OpenAI. I cannot
claim to be the deepest stakeholder in the mathematical community, but I majored in it as
an undergraduate and proved some results about randomized linear algebra over the course of
graduate school. My entire body of graduate work relies on foundations established by
mathematicians, both theoretical and applied, working over decades. 

I have loved mathematics, although I'm not the best at it. I still sorely
regret that I could not crack the AIME round of the AMC math competitions in high school.
Ironically, these olympiad puzzles are now routinely used as benchmarks for large language models. 
Software engineering has undergone a seismic shift in a matter of months. Entire fields of 
computer science, such as programming languages (PL), pivoted on a dime as the 
AI wave took shape from 2022 through 2025. 

I've started this page to blog my observations, and maybe I'll break some of these out into their
own blog posts. I'm not going to claim the authority of, say, 
[Terence Tao's blog](https://terrytao.wordpress.com). The New York Times styles him as a
sort of [army general](https://www.nytimes.com/2026/10/16/us/math-ai-terence-tao.html) as the
mathematical battle lines have been drawn, and I'd fight on his side.

But here, I'm going to focus on junior computer scientists, engineers, and graduate students;
this is a "view from the trenches". I also don't want to add to the noise on social networks like
LinkedIn, which is filled with an army of grifters who, like mosquitoes, suck away
my attention with every narcotizing piece of Claudeslop they mindlessly profligate. That's why I'm
keeping my opinions on this quiet webpage. 

Speaking of LinkedIn: several mathematicians are indignant at 
"carpet-bombing" of mathematics by OpenAI. In turn, posters on LinkedIn have labeled
mathematics as a gatekeeping "cartel". These LinkedIn posters, I can confidently say, 
don't understand any of OpenAI's proofs; they can't, and they won't. I am saddened, however,
by how many people rejoice in steamrolling a quiet community that has asked very little and 
delivered so much to the world.
