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

<div class="chartjs">
  <canvas id="github_contributions"></canvas>

  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/moment@2.27.0"></script>
  <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-moment@0.1.1"></script>

  <script>
    function cssvar(name) {
      return getComputedStyle(document.documentElement).getPropertyValue(name);
    }

    const ctx = document.getElementById('github_contributions');

    const DATA_COUNT = 7;
    const NUMBER_CFG = {count: DATA_COUNT, min: 0, max: 100};

    const data = {
      labels: [new Date(2023, 0, 1), new Date(2023, 0, 2), new Date(2023, 0, 3), new Date(2023, 0, 4), new Date(2023, 0, 5), new Date(2023, 0, 6), new Date(2023, 0, 7)],
      datasets: [{  
        label: 'Dataset with point data',
        backgroundColor: cssvar('--global-theme-color'),
        borderColor: cssvar('--global-theme-color'),
        color: null, 
        fill: false,
        data: [{
          x: new Date(2023, 0, 1), 
          y: 100
        }, {
          x: new Date(2024, 0, 2), 
          y: 200 
        }, {
          x: new Date(2024, 0, 3), 
          y: 50 
        }, {
          x: new Date(2024, 0, 5), 
          y: 200 
        }],
      }]
    };

    const config = {
      type: 'line',
      data: data,
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
              text: 'value'
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
      // Log to the console
      console.log('Chart colors updated');
      chart.update(); 
    } 
  </script>
  </div>
</br>

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
