/* YESPYQ theme — three modes, not two:
     "auto" (default) = dark 19:00–06:00 IST, light otherwise
     "light" / "dark" = user pinned it explicitly
   The old version only stored light/dark, so the first manual tap killed
   auto forever with no way back. Auto is now a first-class choice, and
   while in auto the theme re-evaluates itself so it flips at 19:00 and
   06:00 without needing a reload.
   Exposes window.YQTheme = { get, set, effective, onChange }. */
(function () {
  /* v2 key on purpose. The old system stored only "light"/"dark", so every
     visitor who ever tapped the toggle had a permanent pin saved — and the
     new code would read that as a deliberate choice and never auto-switch
     again. Reading a fresh key retires those legacy pins: everyone starts
     on auto, and only a choice made in the new UI sticks. */
  var KEY = "yespyq_theme_v2";
  var LEGACY_KEY = "yespyq_theme";
  var listeners = [];
  try { localStorage.removeItem(LEGACY_KEY); } catch (e) {}

  function istHour() {
    var d = new Date();
    return new Date(d.getTime() + (d.getTimezoneOffset() + 330) * 60000).getHours();
  }
  function autoTheme() { var h = istHour(); return (h >= 19 || h < 6) ? "dark" : "light"; }

  function get() {                                   // "auto" | "light" | "dark"
    try {
      var s = localStorage.getItem(KEY);
      if (s === "dark" || s === "light" || s === "auto") return s;
    } catch (e) {}
    return "auto";
  }
  function effective() { var m = get(); return m === "auto" ? autoTheme() : m; }

  function apply() {
    var t = effective();
    if (document.documentElement.getAttribute("data-theme") !== t) {
      document.documentElement.setAttribute("data-theme", t);
    }
    return t;
  }
  function set(mode) {
    if (mode !== "auto" && mode !== "light" && mode !== "dark") mode = "auto";
    try { localStorage.setItem(KEY, mode); } catch (e) {}
    var t = apply();
    listeners.forEach(function (fn) { try { fn(mode, t); } catch (e) {} });
    return t;
  }

  window.YQTheme = {
    get: get, set: set, effective: effective,
    onChange: function (fn) { if (typeof fn === "function") listeners.push(fn); }
  };

  apply();                                            // before first paint

  // in auto mode, keep checking so the switch happens on its own
  setInterval(function () { if (get() === "auto") { var b = document.documentElement.getAttribute("data-theme"); if (apply() !== b) listeners.forEach(function (fn) { try { fn("auto", effective()); } catch (e) {} }); } }, 60000);

  /* Small screens used to just hide the nav, leaving no way to navigate.
     Build a drawer instead: brand + PYQ Pass stay visible in the bar, the
     links and the main CTA move behind the ☰ button. Injected here so all
     2,471 pages get it without touching their markup. */
  function buildMobileNav() {
    var bar = document.querySelector(".site-header .header-inner");
    var nav = bar && bar.querySelector(".main-nav");
    if (!bar || !nav || document.getElementById("nav-burger")) return;

    var burger = document.createElement("button");
    burger.id = "nav-burger";
    burger.className = "nav-burger";
    burger.type = "button";
    burger.setAttribute("aria-label", "Menu");
    burger.setAttribute("aria-expanded", "false");
    burger.innerHTML = "<span></span><span></span><span></span>";
    bar.appendChild(burger);

    var drawer = document.createElement("div");
    drawer.id = "nav-drawer";
    drawer.className = "nav-drawer";
    drawer.hidden = true;
    var links = [].map.call(nav.querySelectorAll("a"), function (a) {
      return '<a href="' + a.getAttribute("href") + '"' +
        (a.classList.contains("active") ? ' class="active"' : "") +
        (a.dataset.nav ? ' data-nav="' + a.dataset.nav + '"' : "") +
        ">" + a.textContent.trim() + "</a>";
    }).join("");
    var cta = bar.querySelector(".btn-primary");
    drawer.innerHTML = '<nav class="nd-links">' + links + "</nav>" +
      (cta ? '<a class="nd-cta" href="' + (cta.getAttribute("href") || "#") + '"' +
        (cta.dataset.action ? ' data-action="' + cta.dataset.action + '"' : "") + ">" +
        cta.textContent.trim() + "</a>" : "");
    document.body.appendChild(drawer);

    function close() { drawer.hidden = true; burger.classList.remove("open"); burger.setAttribute("aria-expanded", "false"); document.body.classList.remove("nav-open"); }
    function open() { drawer.hidden = false; burger.classList.add("open"); burger.setAttribute("aria-expanded", "true"); document.body.classList.add("nav-open"); }
    burger.addEventListener("click", function (e) { e.stopPropagation(); drawer.hidden ? open() : close(); });
    drawer.addEventListener("click", function (e) { if (e.target.closest("a")) close(); });
    document.addEventListener("click", function (e) {
      if (!drawer.hidden && !e.target.closest("#nav-drawer") && !e.target.closest("#nav-burger")) close();
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
    window.addEventListener("resize", function () { if (window.innerWidth > 820) close(); });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var b = document.createElement("button");
    b.className = "theme-toggle";
    b.type = "button";
    function icon() {
      var t = effective();
      b.textContent = t === "dark" ? "☀️" : "🌙";
      b.setAttribute("aria-label", t === "dark" ? "Switch to light mode" : "Switch to dark mode");
      b.title = get() === "auto" ? "Auto (by time of day)" : "Theme: " + get();
    }
    icon();
    // the floating button pins the opposite theme; the account menu is
    // where you can put it back on auto
    b.addEventListener("click", function () { set(effective() === "dark" ? "light" : "dark"); icon(); });
    window.YQTheme.onChange(icon);
    document.body.appendChild(b);

    buildMobileNav();

    // load the paywall layer (config → module) once, on every page
    if (!document.getElementById("pay-config-js")) {
      var c = document.createElement("script");
      c.id = "pay-config-js"; c.src = "/pay-config.js?v=6";
      c.onload = function () {
        var m = document.createElement("script"); m.src = "/auth-pay.js?v=22"; m.defer = true;
        document.body.appendChild(m);
      };
      document.body.appendChild(c);
    }
  });
})();
