---
# Leave the homepage title empty to use the site title
title: Vivek Bharadwaj
date: 2022-10-24
type: landing

sections:
  - block: about.avatar
    id: about
    content:
      # Choose a user profile to display (a folder name within `content/authors/`)
      username: admin
      # Override your bio text from `authors/admin/_index.md`? 

    design:
      background:
        # Choose a color such as from https://html-color-codes.info
        # Text color (true=light, false=dark, or remove for the dynamic theme color). 

    design:
      background:
        color: "#C0E0DE"
      spacing:
        padding: ["50px", "0", "10px", "0"]


  - block: collection
    id: publication
    content:
      title: Publications & Preprints
      text: 
      filters:
        folders:
          - publication
        exclude_featured: true 
    design:
      columns: '2'
      view: citation
  - block: collection
    id: talks
    content:
      title: Past & Upcoming Talks
      filters:
        folders:
          - event
    design:
      columns: '2'
      view: compact
  - block: accomplishments 
    content:
      # Note: `&shy;` is used to add a 'soft' hyphen in a long heading.
      title: 'Teaching'
      subtitle: |
        I was a TA for 4 quarters as an undergraduate and
        one semester as a graduate student. Check out the reviews the students
        left me at [this link](post/teaching_reviews/). 
      # Date format: https://wowchemy.com/docs/customization/#date-format
      date_format: Jan 2006
      # Accomplishments.
      #   Add/remove as many `item` blocks below as you like.
      #   `title`, `organization`, and `date_start` are the required parameters.
      #   Leave other parameters empty if not required.
      #   Begin multi-line descriptions with YAML's `|2-` multi-line prefix.
      items:
        - title: "CS267: Applications of Parallel Computing (TA)"
          date_end: '2022-05-17'
          date_start: '2022-01-01'
          description: 'Semester-long course on Parallel Computing.
          Check out my recitation slides and video on optimizing
          GEMM for the Intel Knights Landing processor.' 
          organization: UC Berkeley 
          organization_url: 'https://berkeley.edu' 
          url: "https://sites.google.com/lbl.gov/cs267-spr2022" 
        - title: "CS38: Algorithms (TA)"
          date_end: '2020-06-01'
          date_start: '2020-04-01'
          description: "Proof-based algorithms course. I TA'd three times over
          three years (2018, 2019, 2020), and was awarded the 
          [Thomas A. Tisch Prize for Undergraduate Teaching](https://www.cms.caltech.edu/academics/honors). 
          "
          organization: Caltech 
          organization_url: https://caltech.edu

        - title: 'CS21: Decidability and Tractability (TA)'
          date_end: '2018-04-01'
          date_start: '2018-01-01'
          description: 'Undergraduate complexity theory course.'
          organization: Caltech 
          organization_url: https://caltech.edu
          url: ''
    design:
      columns: '2'
  - block: markdown
    id: service 
    content:
      title: Service
      subtitle: '' 
      text: |      
        * 2022 March: [Reviewer for Berkeley SURF Applications](https://surf.berkeley.edu/): Read applications from undergraduate students seeking
        funded research positions at Berkeley over the summer.
        * 2022 March: Visit Days for SCI Graduate Admissions: Co-organized visit days for programming systems and scientific computing admits, contacted
        admitted students 
        * 2021 October-December: [CRS Science Ambassador](https://crscience.org/educators/): Gave virtual science presentations to students at Washington Elementary, Richmond
        * 2021 January-March: [Virtual Be a Scientist Mentor](https://crscience.org/outreach/basdetails/): Coached BUSD students through science projects weekly
        * 2019-2020: [Caltech Board of Control](https://donut.caltech.edu/lib/BoC_Reps): Member of student panel adjudicating cases of academic dishonesty
        * 2020 Spring: [Caltech RISE Tutor](https://www.caltechy.org/rise-tutor): Tutored underpriveleged high school students from Pasadena Unified School district.
        * 2018: Chair of the Caltech Student Faculty Conference for Computer Science (SFC): Chaired a committee of students and faculty charged with
        making recommendations about the undergraduate computer science program at a conference of students and professors. 
        [Here's our final report.](https://docs.google.com/document/d/e/2PACX-1vQb_tiDPwxd7M485BCGHVAvNjsGADY5sjggVnvqRqZnQe6nzv4nwiHn_GUIIIiaATT2mj7qJ8WonOlf/pub)
        * Judge for the Following High School / Middle School Science Competitions
          * 2023: (Planned) [USA Young Physicists Tournament](https://www.usaypt.org)
          * 2022: [Alameda County Science Fair](https://acsef.zfairs.com)
          * 2021: [USA Young Physicists Tournament](http://www.usaypt.org/)
          * 2020: Blair Middle School Science Fair
    design:
      # See Page Builder docs for all section customization options.
      # Choose how many columns the section has. Valid values: '1' or '2'.
      columns: '2' 
  - block: collection
    id: posts
    content:
      title: Blog Posts 
      subtitle: ''
      text: ''
      # Choose how many pages you would like to display (0 = all pages)
      count: 5
      # Filter on criteria
      filters:
        folders:
          - post
        author: ""
        category: ""
        tag: ""
        exclude_featured: false
        exclude_future: false
        exclude_past: false
        publication_type: ""
      # Choose how many pages you would like to offset by
      offset: 0
      # Page order: descending (desc) or ascending (asc) date.
      order: desc
    design:
      # Choose a layout view
      view: compact
      columns: '2'
---
