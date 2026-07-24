/* YESPYQ theme: dark mode toggle + auto by Indian Standard Time.
   Auto = dark between 19:00 and 06:00 IST; a manual toggle is remembered. */
(function () {
  function istHour() {
    var d = new Date();
    return new Date(d.getTime() + (d.getTimezoneOffset() + 330) * 60000).getHours();
  }
  function preferred() {
    try {
      var s = localStorage.getItem("yespyq_theme");
      if (s === "dark" || s === "light") return s;
    } catch (e) {}
    var h = istHour();
    return (h >= 19 || h < 6) ? "dark" : "light";
  }
  document.documentElement.setAttribute("data-theme", preferred());
  document.addEventListener("DOMContentLoaded", function () {
    var b = document.createElement("button");
    b.className = "theme-toggle";
    b.type = "button";
    b.setAttribute("aria-label", "Toggle dark mode");
    function icon() {
      b.textContent = document.documentElement.getAttribute("data-theme") === "dark" ? "☀️" : "🌙";
    }
    icon();
    b.addEventListener("click", function () {
      var t = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", t);
      try { localStorage.setItem("yespyq_theme", t); } catch (e) {}
      icon();
    });
    document.body.appendChild(b);

    // load the paywall layer (config → module) once, on every page
    if (!document.getElementById("pay-config-js")) {
      var c = document.createElement("script");
      c.id = "pay-config-js"; c.src = "/pay-config.js?v=2";
      c.onload = function () {
        var m = document.createElement("script"); m.src = "/auth-pay.js?v=3"; m.defer = true;
        document.body.appendChild(m);
      };
      document.body.appendChild(c);
    }
  });
})();
