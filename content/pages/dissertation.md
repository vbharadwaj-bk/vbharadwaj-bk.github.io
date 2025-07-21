---
title: dissertation 
template: page 
nav: true 
summary: Information about my PhD exit talk and published work
---
I want to thank everybody attended my dissertation talk - I was
so thrilled to share my work, and I hope anyone who attended found it
interesting. Find the details below!

| Dissertation Talk | Accelerating Multilinear Maps and Structured Sparse Tensor Kernels               |
|-----------------------------|----------------------------------------------------------------------------------|
| Date                        | July 21, 2025                                                                    |
| Time                        | 10:00 AM PDT                                                                     |
| Location                    | 310 Jacobs Hall, UC Berkeley |
| Calendar Invite + Zoom Link | [Click here](https://events.berkeley.edu/events/event/300838-dissertation-talk-accelerating-multilinear-maps#), scroll to "Download to my calendar" |
| Slides                      | [PDF]({static}/pdf/2025/bharadwaj_dissertation_slides.pdf)                          |

</br>


My work explores high-performance algorithms for tensor kernels. 
A *tensor* is a multidimensional array, and a kernel is
a highly optimized piece of mathematical code. Vectors and matrices
are two examples of tensors, but I'm interested in tensors with 3+ 
dimensions. Unfortunately, tensor kernels are underexplored
compared to matrix kernels, both in theory and practice.
My thesis aims to fill that knowledge gap by introducing new
algorithms for one specific tensor kernel, the Matricized
Tensor Times Khatri-Rao Product (MTTKRP). We use
those algorithms to accelerate multiple critical 
applications, as well as a launching pad to study other related problems.

### A PhD by the Numbers
My graduate work was "bursty": it involved long periods of exploration followed by code sprints and paper writing. 
Here's an annotated graph of my average daily Github contributions over time, along with the deadlines for some of the conferences
we submitted our work to: 

!TEMPLATE!
<div class="chartjs" style="aspect-ratio: 2">
  <canvas id="github_contributions"></canvas>

  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/moment@2.27.0"></script>
  <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-moment@0.1.1"></script>

  <script>
    function cssvar(name) {
      return getComputedStyle(document.documentElement).getPropertyValue(name);
    }

    const verticalLinePlugin = {
      getLinePosition: function (chart, pointIndex) {
          const meta = chart.getDatasetMeta(0); // first dataset is used to discover X coordinate of a point
          const data = meta.data;
          return data[pointIndex].x;
      },

      renderVerticalLine: function (chartInstance, pointIndex, label) {
          const lineLeftOffset = this.getLinePosition(chartInstance, pointIndex);
          const scale = chartInstance.scales.y;
          const context = chartInstance.ctx;
          // render vertical line
          context.beginPath();
          context.strokeStyle = '#ff0000';
          context.moveTo(lineLeftOffset, scale.top);
          context.lineTo(lineLeftOffset, scale.bottom);
          context.stroke();

          // write label
          context.fillStyle = "#ff0000";
          context.textAlign = 'center';
          context.fillText(label, lineLeftOffset, (scale.bottom - scale.top) / 9 + scale.top);
      },

      beforeDatasetsDraw: function (chart, easing) {
          if(chart.config._config.lineAtIndex)
              chart.config._config.lineAtIndex.forEach(pointIndex => this.renderVerticalLine(chart, pointIndex[0], pointIndex[1]));
      }
    };

    const ctx = document.getElementById('github_contributions');

    function Get(yourUrl){
      var Httpreq = new XMLHttpRequest(); // a new request
      Httpreq.open("GET",yourUrl,false);
      Httpreq.send(null);
      return Httpreq.responseText;          
    }

    var gh_json = JSON.parse(Get("{{ 'json/phd_github_activity.json' | relative_url}}"));

    const data = {
      datasets: [{  
        label: '28-Day Moving Average GH Daily Contributions',
        backgroundColor: null, 
        borderColor: null,
        borderWidth: 0.8, 
        color: null, 
        fill: false,
        data: gh_json['data'],
        pointRadius: 0,
        tension: 0.1
      }]
    };

    const config = {
      type: 'line',
      data: data,
      lineAtIndex: gh_json['milestones'],
      plugins: [verticalLinePlugin],
      options: {
        plugins: {
          legend: {
            labels: {color: null}
          }
        },
        scales: {
          x: {
            type: 'time',
            time: {
              // Luxon format string
              tooltipFormat: 'DD T'
            },
            title: {
              display: true,
              text: 'Date'
            },
            ticks: {color: null},
            grid: {color: null}
          },
          y: {
            title: {
              display: true,
              text: 'Avg. Daily Contributions'
            },
            ticks: {color: null},
            grid: {color: null}
          }
        },
      },
    };

    function modifyChartColors(config, data) {
      let globalTextColor = cssvar('--global-text-color');
      let chartGridColor = cssvar('--chart-grid-color');

      global_color_fields = [
        config.options.scales.x.ticks,
        config.options.scales.y.ticks,
        config.options.scales.x.title,
        config.options.scales.y.title,
        config.options.plugins.legend.labels
      ]

      grey_fields = [
        config.options.scales.x.grid,
        config.options.scales.y.grid,
      ]

      data.datasets.forEach((dataset) => {
        dataset.backgroundColor = cssvar('--global-theme-color'); 
        dataset.borderColor = cssvar('--global-theme-color'); 
      });

      global_color_fields.forEach((field) => {
        field.color = globalTextColor;
      });

      grey_fields.forEach((field) => {
        field.color = chartGridColor; 
      });
    }

    modifyChartColors(config, config.data);
    let chart = new Chart(ctx, config);

    chart.canvas.parentNode.refreshChart = function() {
      modifyChartColors(chart.config, chart.data);
      chart.update(); 
    } 
  </script>
  </div>
</br>
!TEMPLATE!

Here are some statistics from the past five years. 
Some numbers (like thesis page count, research diary length, or 
Github contributions) are pointless and clearly influenced 
by noise. Others, I'm very proud of. 

| Statistic | Quantity |
| -------- | --------------- |
| Piazza forum contributions as a CS267 teaching assistant | 831 |
| Powerpoint slides in research diary | 630+ |
| Total dissertation page count (incl. frontmatter + references) | 182 |
| BeBOP + PASSION group presentations | 35 |
| Domestic + international conference trips | 15 |
| Semesters at Berkeley, including summers | 14 |
| Non-research classes taken | 8 |
| Published papers | 5 |
| Summer internships | 2 |
| PhDs (almost) earned | 1 |
</br>