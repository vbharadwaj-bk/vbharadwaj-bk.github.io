$(document).ready(function() {
  // add toggle functionality to abstract and bibtex buttons
  $('a.abstract').click(function() {
    $(this).parent().parent().find(".abstract.hidden").toggleClass('open');
    $(this).parent().parent().find(".bibtex.hidden.open").toggleClass('open');
  });
  $('a.bibtex').click(function() {
    $(this).parent().parent().find(".bibtex.hidden").toggleClass('open');
    $(this).parent().parent().find(".abstract.hidden.open").toggleClass('open');
  });
  $('a').removeClass('waves-effect waves-light');

  // Normalize custom titles, e.g. "!!! theorem \"X\"" -> "Theorem (X)"
  [['definition', 'Definition'], ['theorem', 'Theorem']].forEach(function(entry) {
    const typeClass = entry[0];
    const baseTitle = entry[1];
    $(`.admonition.${typeClass} .admonition-title`).each(function() {
      const currentTitle = $(this).text().trim();
      if (!currentTitle || currentTitle === baseTitle) {
        return;
      }
      const alreadyNormalized = new RegExp(`^${baseTitle}\\s*\\(.+\\)$`);
      if (alreadyNormalized.test(currentTitle)) {
        return;
      }
      $(this).text(`${baseTitle} (${currentTitle})`);
    });
  });

  // bootstrap-toc
  if($('#toc-sidebar').length){
    let navbarHeight = $("#navbar").outerHeight(true);
    var navSelector = "#toc-sidebar";
    var $myNav = $(navSelector);
    Toc.init($myNav);
    $("body").scrollspy({
      target: navSelector,
      offset: navbarHeight*1.29, 
    });
  }

  // add css to jupyter notebooks
  const cssLink = document.createElement("link");
  cssLink.href  = "../css/jupyter.css";
  cssLink.rel   = "stylesheet";
  cssLink.type  = "text/css";

  let theme = localStorage.getItem("theme");
  if (theme == null || theme == "null") {
    const userPref = window.matchMedia;
    if (userPref && userPref("(prefers-color-scheme: dark)").matches) {
      theme = "dark";
    }
  }

  $('.jupyter-notebook-iframe-container iframe').each(function() {
    $(this).contents().find("head").append(cssLink);

    if (theme == "dark") {
      $(this).bind("load",function(){
        $(this).contents().find("body").attr({
          "data-jp-theme-light": "false",
          "data-jp-theme-name": "JupyterLab Dark"});
      });
    }
  });
});

