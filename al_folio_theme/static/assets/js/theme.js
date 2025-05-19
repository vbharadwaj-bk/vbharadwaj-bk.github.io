// Has to be in the head tag, otherwise a flicker effect will occur.

let toggleTheme = (theme) => {
  if (theme == "dark") {
    setTheme("light");
  } else {
    setTheme("dark");
  }
};

let setTheme = (theme) => {
  transTheme();
  setHighlight(theme);

  if (theme) {
    document.documentElement.setAttribute("data-theme", theme);

    // Add class to tables.
    let tables = document.getElementsByTagName("table");
    for (let i = 0; i < tables.length; i++) {
      if (theme == "dark") {
        tables[i].classList.add("table-dark");
      } else {
        tables[i].classList.remove("table-dark");
      }
    }

    // Set jupyter notebooks themes.
    let jupyterNotebooks = document.getElementsByClassName("jupyter-notebook-iframe-container");
    for (let i = 0; i < jupyterNotebooks.length; i++) {
      let bodyElement = jupyterNotebooks[i].getElementsByTagName("iframe")[0].contentWindow.document.body;
      if (theme == "dark") {
        bodyElement.setAttribute("data-jp-theme-light", "false");
        bodyElement.setAttribute("data-jp-theme-name", "JupyterLab Dark");
      } else {
        bodyElement.setAttribute("data-jp-theme-light", "true");
        bodyElement.setAttribute("data-jp-theme-name", "JupyterLab Light");
      }
    }

    let charts = document.getElementsByClassName("chartjs");
    for (let i = 0; i < charts.length; i++) {
      //charts[i].refreshChart();
    }

  } else {
    document.documentElement.removeAttribute("data-theme");
  }

  localStorage.setItem("theme", theme);

  // Updates the background of medium-zoom overlay.
  if (typeof medium_zoom !== "undefined") {
    medium_zoom.update({
      background:
        getComputedStyle(document.documentElement).getPropertyValue(
          "--global-bg-color"
        ) + "ee", // + 'ee' for trasparency.
    });
  }
};

let setHighlight = (theme) => {
  if (theme == "dark") {
    document.getElementById("highlight_theme_light").media = "none";
    document.getElementById("highlight_theme_dark").media = "";
  } else {
    document.getElementById("highlight_theme_dark").media = "none";
    document.getElementById("highlight_theme_light").media = "";
  }
};

let transTheme = () => {
  document.documentElement.classList.add("transition");
  window.setTimeout(() => {
    document.documentElement.classList.remove("transition");
  }, 500);
};

let initTheme = (theme) => {
  if (theme == null || theme == "null") {
    theme = "dark";
  }

  var nonce = localStorage.getItem("nonce");
  if (nonce == null || nonce == "null" || nonce == 1) {
    theme = "dark";
    localStorage.setItem("nonce", 2);
  }

  setTheme(theme);
};

initTheme(localStorage.getItem("theme"));