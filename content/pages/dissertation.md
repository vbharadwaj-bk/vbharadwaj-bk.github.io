---
title: dissertation 
template: page 
nav: true 
summary: Information about my PhD exit talk and published work
---
I'm excited to graduate with
my PhD in computer science from UC Berkeley. If you would
like to attend my exit talk on August 13, 2025, please send me
an email!

### My PhD by the Numbers
PhD work is "bursty": in computer science, it involves long periods of exploration 
followed by high-intensity code sprints and paper writing. 
Here's an annotated graph of my average daily Github contributions over time: 

!TEMPLATE!
<div class="chartjs">
  <canvas id="github_contributions"></canvas>

  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/moment@2.27.0"></script>
  <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-moment@0.1.1"></script>
  <script src="https://cdn.jsdelivr.net/npm/hammerjs@2.0.8"></script>
  <script src="
https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@2.2.0/dist/chartjs-plugin-zoom.min.js
"></script>

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
        color: null, 
        fill: false,
        data: gh_json['data'],
        pointRadius: 0
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
          },
          zoom: {
              zoom: {
                  wheel: {
                    enabled: true,
                  },
                  pinch: {
                    enabled: true
                  },
                  mode: 'xy',
                }
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
| Total dissertation page count (incl. frontmatter + references) | 160+ |
| BeBOP + PASSION group presentations | 35 |
| Domestic + international conference trips | 18 |
| Semesters at Berkeley, including summer | 14 |
| Non-research classes taken | 8 |
| Published papers | 5 |
| Summer internships | 2 |
| PhDs (almost) earned | 1 |
</br>