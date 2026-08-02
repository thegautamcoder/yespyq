/* ============================================================
   YESPYQ — auth + payment layer (soft paywall), site-wide.
   Loaded on EVERY page (via theme.js). It:
     • injects the "PYQ Pass" button into the header
     • renders the shiny unlock popup + floating pill
     • auto-opens the popup after N seconds on site
     • runs Google sign-in (Supabase) + Razorpay checkout
   Supabase/Razorpay SDKs load lazily (only when needed) so content
   pages stay fast. The Razorpay SECRET is never here — it lives only
   in the Supabase Edge Functions.

   Exposes window.PAY: isPaid(), gateContent(), freeQuestions(),
   freeQuizzesPerDay(), openUnlock(context), startCheckout(), signOut().
   Fires window.onPayChange() when paid/login state changes.
   ============================================================ */
(function () {
  "use strict";
  var cfg = window.PAY_CONFIG || {};
  var SHOW = cfg.SHOW_POPUP !== false;
  var GATE = !!cfg.GATE_CONTENT;

  function ph(v, needle) { return v && v.indexOf(needle) === -1; }
  // auth (Supabase) and payment (Razorpay) readiness are independent:
  // sign-in can work before the Razorpay key is filled in.
  function authReady() { return ph(cfg.SUPABASE_URL, "YOUR-PROJECT") && ph(cfg.SUPABASE_ANON_KEY, "YOUR_"); }
  function backendReady() { return authReady() && ph(cfg.RAZORPAY_KEY_ID, "YOUR"); }
  var FUNCS = (cfg.FUNCTIONS_BASE || (cfg.SUPABASE_URL || "") + "/functions/v1").replace(/\/$/, "");
  var INTENT = "yespyq_pay_intent";

  var sb = null, _user = null, _paid = false, _exp = null, _expired = false;

  function daysLeft() { return _exp ? Math.max(0, Math.ceil((_exp - Date.now()) / 86400000)) : 0; }
  function expDate() { return _exp ? new Date(_exp).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" }) : ""; }

  function notify() { try { if (typeof window.onPayChange === "function") window.onPayChange(); } catch (e) {} }

  window.PAY = {
    isPaid: function () { return GATE ? _paid : true; },   // ungated → everyone "has access"
    gateContent: function () { return GATE; },
    user: function () { return _user; },
    freeQuestions: function () { return cfg.FREE_QUESTIONS || 20; },
    freeQuizzesPerDay: function () { return cfg.FREE_QUIZZES_PER_DAY || 1; },
    openUnlock: openUnlock,
    startCheckout: startCheckout,
    signOut: signOut
  };

  /* ---------- lazy SDK loaders ---------- */
  function loadScript(src) {
    return new Promise(function (res, rej) {
      var s = document.createElement("script"); s.src = src; s.async = true;
      s.onload = res; s.onerror = rej; document.head.appendChild(s);
    });
  }
  async function ensureSb() {
    if (sb) return sb;
    if (!window.supabase) await loadScript("https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2");
    sb = window.supabase.createClient(cfg.SUPABASE_URL, cfg.SUPABASE_ANON_KEY);
    sb.auth.onAuthStateChange(function (_e, session) {
      _user = session ? session.user : null;
      if (_user) refreshEntitlement().then(function () { recordLogin(); startActivityTimer(); renderChrome(); notify(); });
      else { _paid = false; renderChrome(); notify(); }
    });
    return sb;
  }
  var _rzpLoading = null;
  function ensureRzp() {
    if (window.Razorpay) return Promise.resolve();
    if (!_rzpLoading) _rzpLoading = loadScript("https://checkout.razorpay.com/v1/checkout.js");
    return _rzpLoading;
  }

  /* ---------- "we're getting your payment ready" overlay ----------
     Returning from Google there is a real gap (restore session, check
     entitlement, load Razorpay, create the order). Left blank, people
     assume it failed and leave — so say what's happening straight away. */
  var _loader = null;
  function showPayLoader(msg) {
    if (_loader) { if (msg) setLoaderMsg(msg); return; }
    _loader = document.createElement("div");
    _loader.className = "pay-loader";
    _loader.innerHTML =
      '<div class="pl-card">' +
        '<div class="pl-crown">PYQ Pass</div>' +
        '<div class="pl-spin" aria-hidden="true"></div>' +
        '<div class="pl-msg">' + escapeH(msg || "Signing you in…") + '</div>' +
        '<div class="pl-sub">Opening secure payment · ₹149 for 1 year</div>' +
        '<div class="pl-trust">Secured by Razorpay</div>' +
      '</div>';
    document.body.appendChild(_loader);
    requestAnimationFrame(function () { if (_loader) _loader.classList.add("in"); });
  }
  function setLoaderMsg(msg) {
    var m = _loader && _loader.querySelector(".pl-msg");
    if (m) m.textContent = msg;
  }
  function hidePayLoader() {
    if (!_loader) return;
    var l = _loader; _loader = null;
    l.classList.remove("in");
    setTimeout(function () { if (l.parentNode) l.parentNode.removeChild(l); }, 200);
  }

  async function refreshEntitlement() {
    if (!_user || !sb) { _paid = false; _exp = null; _expired = false; return; }
    try {
      var r = await sb.from("entitlements").select("paid,expires_at").eq("user_id", _user.id).maybeSingle();
      var row = r && r.data;
      _exp = row && row.expires_at ? Date.parse(row.expires_at) : null;
      var valid = !_exp || _exp > Date.now();        // no expiry recorded = legacy lifetime
      _paid = !!(row && row.paid && valid);
      _expired = !!(row && row.paid && _exp && _exp <= Date.now());
    } catch (e) { _paid = false; _exp = null; _expired = false; }
  }
  async function accessToken() {
    if (!sb) return null;
    var r = await sb.auth.getSession();
    return r && r.data && r.data.session ? r.data.session.access_token : null;
  }

  /* ---------- restore an existing login (only if one exists) ---------- */
  function hasStoredSession() {
    try { for (var i = 0; i < localStorage.length; i++) { var k = localStorage.key(i); if (/^sb-.*-auth-token$/.test(k)) return true; } } catch (e) {}
    return false;
  }
  /* Returning from Google, the session arrives in the URL (hash for the
     implicit flow, ?code= for PKCE) BEFORE it exists in localStorage — so
     we must boot Supabase for that too, or the login silently drops. */
  function hasOAuthCallback() {
    return /[#&]access_token=|[#&]error=/.test(location.hash || "") ||
           /[?&]code=/.test(location.search || "");
  }
  async function initSession() {
    if (!authReady()) return;
    if (!hasStoredSession() && !hasOAuthCallback()) return;
    // coming back from Google mid-purchase: show the loader immediately,
    // and start fetching Razorpay's SDK in the background right away
    var resuming = hasOAuthCallback() && localStorage.getItem(INTENT);
    if (resuming && SHOW) { showPayLoader("Signing you in…"); ensureRzp(); }
    try {
      await ensureSb();
      var res = await sb.auth.getSession();
      var session = res && res.data && res.data.session;
      if (session) { _user = session.user; await refreshEntitlement(); recordLogin(); startActivityTimer(); renderChrome(); notify(); }
      // tidy the tokens out of the address bar once they're stored
      if (session && hasOAuthCallback() && history.replaceState) {
        history.replaceState({}, document.title, location.pathname + location.search.replace(/[?&]code=[^&]*/, ""));
      }
      if (_user && !_paid && localStorage.getItem(INTENT)) { localStorage.removeItem(INTENT); startCheckout(); return; }
      hidePayLoader();   // signed in but nothing to resume
      // plan ran out → tell the user once per session and re-lock content
      if (_expired && SHOW && !sessionStorage.getItem("yespyq_renew_shown")) {
        sessionStorage.setItem("yespyq_renew_shown", "1");
        openUnlock("expired");
      }
    } catch (e) { hidePayLoader(); }
  }

  /* ---------- auth ---------- */
  /* wantsToBuy=true  → resume checkout automatically after the redirect
     wantsToBuy=false → "Already paid? Sign in": restore access only, and
     never push a returning customer into paying again. */
  async function signInWithGoogle(wantsToBuy) {
    if (!authReady()) { comingSoon(); return; }
    track("signin_started", { intent: wantsToBuy ? "buy" : "restore" });
    if (wantsToBuy) localStorage.setItem(INTENT, "1");
    else localStorage.removeItem(INTENT);
    await ensureSb();
    sb.auth.signInWithOAuth({ provider: "google", options: { redirectTo: location.origin + location.pathname } });
  }
  async function signOut() { try { if (sb) await sb.auth.signOut(); } catch (e) {} _user = null; _paid = false; renderChrome(); notify(); }

  /* ---------- analytics: logins + time on site ----------
     Writes go through SECURITY DEFINER RPCs keyed on auth.uid(),
     so a user can only ever record their own activity. */
  /* NOTE: supabase-js builders are lazy — rpc() only performs the request
     once it is awaited/then-ed. Calling it fire-and-forget silently does
     nothing, which is why logins and activity were never recorded. Always
     attach .then(). */
  function rpc(fn, args) {
    if (!sb) return Promise.resolve();
    try {
      return Promise.resolve(sb.rpc(fn, args)).then(function (r) {
        if (r && r.error) console.warn("[YESPYQ] rpc " + fn + " failed:", r.error.message);
        return r;
      }, function (e) { console.warn("[YESPYQ] rpc " + fn + " threw:", e); });
    } catch (e) { return Promise.resolve(); }
  }

  function recordLogin() {
    if (!sb || !_user) return;
    // one login event per browser session, not per page view
    if (sessionStorage.getItem("yespyq_login_logged")) return;
    sessionStorage.setItem("yespyq_login_logged", "1");
    // reuse the same per-browser id used for anonymous events as the
    // "device id" — lets us tell a repeat visit on the same browser from
    // a genuinely new one, and spot one device signing into several
    // accounts (a proxy for account sharing), without fingerprinting
    rpc("record_login", { p_user_agent: navigator.userAgent.slice(0, 300), p_device_id: anonId() });
    track("signin_completed", { paid: _paid });
  }

  /* ---------- product events (works logged-out too) ---------- */
  function anonId() {
    try {
      var k = "yespyq_anon", v = localStorage.getItem(k);
      if (!v) { v = "a_" + Date.now().toString(36) + Math.random().toString(36).slice(2, 9); localStorage.setItem(k, v); }
      return v;
    } catch (e) { return null; }
  }
  function track(event, props) {
    if (!authReady()) return Promise.resolve();
    // events must fire for anonymous visitors too — they are the drop-offs
    return ensureSb().then(function () {
      return rpc("track_event", {
        p_event: event,
        p_props: props || {},
        p_path: location.pathname.slice(0, 300),
        p_anon_id: anonId(),
        p_referrer: (document.referrer || "").slice(0, 300)
      });
    }, function () {});
  }
  window.PAY.track = track;

  var _acc = 0, _tick = null;
  function flushActivity() {
    var secs = Math.round(_acc);
    if (!sb || !_user || secs < 5) return;
    _acc = 0;
    rpc("record_activity", { p_seconds: secs });
  }
  function startActivityTimer() {
    if (_tick || !_user) return;
    _tick = setInterval(function () {
      if (document.visibilityState === "visible") _acc += 15;
      if (_acc >= 60) flushActivity();               // flush at least once a minute
    }, 15000);
    // best-effort flush when the tab is hidden or the user navigates away
    document.addEventListener("visibilitychange", function () {
      if (document.visibilityState === "hidden") flushActivity();
    });
    window.addEventListener("pagehide", flushActivity);
  }


  /* ---------- payment ---------- */
  async function startCheckout() {
    if (!authReady()) { comingSoon(); return; }
    if (!_user) { await signInWithGoogle(true); return; }  // buying: resume checkout after redirect
    if (!backendReady()) { comingSoon(); return; }          // signed in, but payments not live yet
    // load Razorpay's SDK *while* the order is being created, not after —
    // the two are independent and doing them in series wastes a second
    var rzpReady = ensureRzp();
    setBusy(true);
    setLoaderMsg("Setting up your payment…");
    var token = await accessToken(), order;
    try {
      var resp = await fetch(FUNCS + "/create-order", {
        method: "POST", headers: { "Content-Type": "application/json", "Authorization": "Bearer " + token }, body: "{}"
      });
      order = await resp.json();
      if (!resp.ok || !order.id) throw new Error(order && order.error ? order.error : "HTTP " + resp.status);
    } catch (e) {
      setBusy(false);
      if (!overlay) openUnlock("error");
      hidePayLoader();
      var why = (e && e.message) ? String(e.message) : "unknown error";
      track("order_failed", { reason: why });
      console.error("[YESPYQ] create-order failed:", why);
      alert("Could not start payment.\n\nReason: " + why + "\n\nPlease screenshot this and email teamyespyq@gmail.com.");
      return;
    }

    // the SDK has been loading alongside the order — make sure it's ready
    try { await rzpReady; } catch (e) {}
    if (typeof window.Razorpay !== "function") {
      hidePayLoader(); setBusy(false);
      if (!overlay) openUnlock("error");
      alert("Payment library failed to load. Please check your connection and try again.");
      return;
    }

    var rzp = new window.Razorpay({
      key: cfg.RAZORPAY_KEY_ID, order_id: order.id, amount: order.amount, currency: order.currency || "INR",
      name: "YESPYQ PYQ Pass", description: "1-year access — all PYQs & explanations",
      image: "https://yespyq.com/assets/favicon.svg", theme: { color: "#2563eb" },
      // we already know who they are from Google — don't ask for a phone
      // number, and don't let them type a different email than the account
      // the entitlement will be written against
      prefill: { email: _user.email || "" },
      readonly: { email: true },
      hidden: { contact: true },
      handler: async function (r) {
        setBusy(true, "Verifying…");
        try {
          var vr = await fetch(FUNCS + "/verify-payment", {
            method: "POST", headers: { "Content-Type": "application/json", "Authorization": "Bearer " + token },
            body: JSON.stringify({ razorpay_order_id: r.razorpay_order_id, razorpay_payment_id: r.razorpay_payment_id, razorpay_signature: r.razorpay_signature })
          });
          var vj = await vr.json();
          if (vr.ok && vj.paid) { _paid = true; onPaid(); } else throw 0;
        } catch (e) { alert("Payment received but verification failed. Email teamyespyq@gmail.com with your payment id."); }
        setBusy(false);
      },
      // closing the Razorpay window shouldn't quietly drop them onto the
      // site — bring the paywall back so the next step is obvious
      modal: { ondismiss: function () { setBusy(false); hidePayLoader(); track("checkout_dismissed", {}); if (!_paid) openUnlock("dismissed"); } }
    });
    rzp.on("payment.failed", function (r) { setBusy(false); hidePayLoader(); track("payment_failed", { reason: (r && r.error && r.error.description) || "" }); alert("Payment failed or cancelled."); });
    setBusy(false);
    track("checkout_started", { order_id: order.id, amount: order.amount });
    rzp.open();
    hidePayLoader();                      // Razorpay is on screen now
  }
  function onPaid() { track("payment_success", {}); refreshEntitlement().then(function(){ closeUnlock(); renderChrome(); notify(); showToast("PYQ Pass active for 1 year — everything's unlocked!"); }); }
  function comingSoon() { showToast("PYQ Pass is launching very soon — thanks for your interest!"); }

  /* ============================================================
     UI
     ============================================================ */
  var overlay = null;

  /* inject the PYQ Pass button into the header on every page */
  function injectHeaderButton() {
    var bar = document.querySelector(".site-header .header-inner");
    if (!bar || bar.querySelector("[data-unlock='header']")) return;
    var a = document.createElement("a");
    a.href = "#"; a.className = "btn btn-premium btn-sm"; a.setAttribute("data-unlock", "header");
    a.innerHTML = "PYQ Pass";
    var cta = bar.querySelector(".btn-primary");
    if (cta) bar.insertBefore(a, cta); else bar.appendChild(a);
  }

  function renderChrome() {
    if (!SHOW) return;
    injectHeaderButton();
    // the floating rotating pill was cut — a single clear header CTA
    // (PYQ Pass) is the one persistent upsell now, no floating nag.
    var pill = document.getElementById("pay-pill");
    if (pill) pill.remove();
    document.querySelectorAll("[data-unlock='header']").forEach(function (el) { el.style.display = _paid ? "none" : ""; });
    renderAccount();
    renderPromos();
  }

  /* In-page promos on content pages: a sticky rail in the empty side
     margin (desktop) + an inline banner after the first content block.
     Both vanish once the user is premium. */
  /* A line under every revealed solution — the highest-intent moment on
     the site, since they've just read one explanation and want the rest. */
  function nudgeHTML() {
    if (_paid || !SHOW) return "";
    return '<div class="sol-nudge">' +
      '<span class="sn-t">Liked this explanation? <b>19,200+ more</b>, every one solved.</span>' +
      '<button class="sn-cta" data-unlock="solution">Get PYQ Pass · ' + (cfg.PRICE_LABEL || "₹149") + '</button>' +
    '</div>';
  }
  window.PAY.nudgeHTML = nudgeHTML;

  function injectSolutionNudges() {
    if (_paid || !SHOW) {
      document.querySelectorAll(".sol-nudge").forEach(function (n) { n.remove() });
      return;
    }
    document.querySelectorAll(".exp-body").forEach(function (body) {
      var host = body.parentNode;
      if (!host || host.querySelector(":scope > .sol-nudge")) return;
      host.insertAdjacentHTML("beforeend", nudgeHTML());
    });
  }

  function renderPromos() {
    injectSolutionNudges();
    var oldRail = document.getElementById("promo-rail"); if (oldRail) oldRail.remove(); // retired
    if (_paid) {
      var oldb = document.getElementById("promo-band"); if (oldb) oldb.remove();
      return;
    }
    if (!SHOW) return;
    var price = cfg.PRICE_LABEL || "₹149";
    var isHome = !!document.getElementById("view-home");   // SPA homepage handles its own CTAs
    var isPassPage = /\/pyq-pass\/?$/.test(location.pathname); // Pass page has its own buy card

    // inline banner mid-content — skip home + dedicated Pass page
    if (!isHome && !isPassPage && !document.getElementById("promo-band")) {
      // descend past single-child wrappers (main > .container > …) to the
      // element that actually holds the page's content blocks
      var host = document.querySelector("main") || document.querySelector(".site-main");
      while (host && host.children.length === 1 && host.firstElementChild &&
             /^(DIV|SECTION)$/.test(host.firstElementChild.tagName)) {
        host = host.firstElementChild;
      }
      if (host) {
        var blocks = [].filter.call(host.children, function (el) {
          return /^(SECTION|ARTICLE|DIV|UL|OL|TABLE)$/.test(el.tagName) && el.offsetHeight > 40;
        });
        // sit after the 2nd block, but never as the very last thing on the page
        var anchor = blocks.length >= 3 ? blocks[1] : (blocks.length ? blocks[0] : null);
        if (anchor) {
          var band = document.createElement("div");
          band.id = "promo-band"; band.className = "promo-band";
          band.innerHTML =
            '<div class="pb-left">' +
              '<div><b>Unlock every PYQ, every explanation</b>' +
              '<em>UPSC · SSC · JEE · NEET · Boards — ' + price + ' for a full year</em></div>' +
            '</div>' +
            '<div class="pb-right">' +
              '<button class="pb-cta" data-unlock="band">Get PYQ Pass</button>' +
              '<button class="pb-signin" data-unlock-signin>Already paid?</button>' +
            '</div>';
          anchor.parentNode.insertBefore(band, anchor.nextSibling);
        }
      }
    }
  }

  /* account chip (right side of header): plan status, days left, renew, sign out */
  function renderAccount() {
    var bar = document.querySelector(".site-header .header-inner");
    var acct = document.getElementById("pay-acct");
    if (!_user) { if (acct) acct.remove(); return; }
    if (!bar) return;
    if (!acct) {
      acct = document.createElement("div");
      acct.id = "pay-acct"; acct.className = "acct";
      bar.appendChild(acct);
    }
    var email = _user.email || "";
    var initial = (email[0] || "U").toUpperCase();
    var plan, planCls, renewBtn = "";
    if (_paid) {
      var d = daysLeft();
      plan = "PYQ Pass · " + d + " day" + (d === 1 ? "" : "s") + " left";
      planCls = d <= 30 ? "warn" : "ok";
      if (d <= 30) renewBtn = '<button class="acct-renew" data-unlock-buy>Renew now · ' + (cfg.PRICE_LABEL || "₹149") + '</button>';
      plan += _exp ? '<em>expires ' + expDate() + '</em>' : "";
    } else if (_expired) {
      plan = "Plan expired" + (_exp ? '<em>on ' + expDate() + '</em>' : "");
      planCls = "no";
      renewBtn = '<button class="acct-renew" data-unlock-buy>Renew · ' + (cfg.PRICE_LABEL || "₹149") + '</button>';
    } else {
      plan = "Free plan";
      planCls = "";
      renewBtn = '<button class="acct-renew" data-unlock="acct">Upgrade · ' + (cfg.PRICE_LABEL || "₹149") + '</button>';
    }
    var mode = (window.YQTheme && window.YQTheme.get()) || "auto";
    var themeRow = '<div class="acct-theme"><span class="at-lbl">Appearance</span><div class="at-seg">' +
      ["auto", "light", "dark"].map(function (m) {
        return '<button class="at-opt' + (mode === m ? " on" : "") + '" data-theme-set="' + m + '">' +
          (m === "auto" ? "Auto" : m === "light" ? "☀️" : "🌙") + '</button>';
      }).join("") + '</div></div>';

    acct.innerHTML =
      '<button class="acct-btn ' + (_paid ? "paid" : "") + '" data-acct-toggle aria-label="Account">' + escapeH(initial) + '</button>' +
      '<div class="acct-menu" hidden>' +
        '<div class="acct-email">' + escapeH(email) + '</div>' +
        '<div class="acct-plan ' + planCls + '">' + plan + '</div>' +
        renewBtn +
        themeRow +
        '<button class="acct-out" data-pay-signout>Sign out</button>' +
      '</div>';
  }

  /* Short, scannable value list — three lines, no reading fatigue */
  function valueList() {
    return [
      '<div class="mp-exams" aria-label="Exams included">' +
        '<span>UPSC</span><span>JEE</span><span>NEET</span><span>SSC CGL</span><span>Defence</span><span>Boards</span>' +
      '</div>',
      '<ul class="unlock-feats">',
      '<li><span class="uf-ck">✓</span>19,200+ PYQs, every one explained</li>',
      '<li><span class="uf-ck">✓</span>Unlimited quizzes, all subjects &amp; years</li>',
      '<li><span class="uf-ck">✓</span>New questions added at no extra cost</li>',
    '</ul>'].join("");
  }

  function openUnlock(context) {
    if (!SHOW || _paid || overlay) return;
    var renewing = context === "expired" || _expired;
    track("paywall_shown", { context: context || "cta", renewing: renewing, signed_in: !!_user });
    overlay = document.createElement("div");
    overlay.className = "unlock-overlay";
    var loggedIn = !!_user;
    var price = cfg.PRICE_LABEL || "₹149";
    var cta = renewing ? "Renew · " + price : "Unlock PYQ Pass →";
    var sub = renewing ? "Another full year, same price" : "Pay once · unlocked in seconds";
    var h2 = renewing ? "Welcome back — your plan has expired"
      : "Every PYQ. Every exam. One key.";
    var tag = renewing ? "Renew to keep everything unlocked."
      : "One pass, one year, all exams, all PYQs";
    overlay.innerHTML =
      '<div class="unlock-card" role="dialog" aria-modal="true">' +
        '<button class="unlock-x" data-unlock-close aria-label="Close">×</button>' +
        '<div class="unlock-banner">PYQ PASS</div>' +
        '<div class="unlock-main">' +
          '<div class="unlock-left">' +
            '<h2>' + h2 + '</h2>' +
            '<p class="unlock-tag">' + tag + '</p>' +
            valueList() +
          '</div>' +
          '<div class="unlock-right">' +
            '<div class="offer-chip">Launch price · 70% off</div>' +
            '<div class="unlock-price"><span class="up-was">₹499</span><span class="up-amt">' + price + '</span><span class="up-note">one-time · valid 1 year</span></div>' +
            '<button class="unlock-cta" data-unlock-buy><span class="uc-glow"></span>' + escapeH(cta) + '</button>' +
            '<p class="unlock-sub">' + escapeH(sub) + '</p>' +
            '<div class="unlock-trust">Razorpay secure · Instant access</div>' +
            (loggedIn ? '' : '<p class="unlock-restore">Already paid? <a href="#" data-unlock-signin>Sign in</a></p>') +
          '</div>' +
        '</div>' +
      '</div>';
    document.body.appendChild(overlay);
    document.body.style.overflow = "hidden";
    requestAnimationFrame(function () { overlay.classList.add("in"); });
  }
  function closeUnlock() {
    if (!overlay) return;
    if (!_paid) track("paywall_dismissed", { signed_in: !!_user });
    overlay.classList.remove("in"); var o = overlay; overlay = null;
    document.body.style.overflow = "";
    setTimeout(function () { if (o && o.parentNode) o.parentNode.removeChild(o); }, 200);
  }
  function setBusy(on, msg) {
    var btn = overlay && overlay.querySelector(".unlock-cta");
    if (!btn) return;
    btn.disabled = !!on; btn.classList.toggle("busy", !!on);
    if (on && msg) { btn.dataset.prev = btn.dataset.prev || btn.textContent; btn.textContent = msg; }
    else if (!on && btn.dataset.prev) { btn.textContent = btn.dataset.prev; delete btn.dataset.prev; }
  }
  function showToast(t) {
    var el = document.createElement("div"); el.className = "pay-toast"; el.textContent = t;
    document.body.appendChild(el);
    requestAnimationFrame(function () { el.classList.add("in"); });
    setTimeout(function () { el.classList.remove("in"); setTimeout(function () { el.remove(); }, 300); }, 3400);
  }
  function escapeH(s) { return String(s).replace(/[&<>"]/g, function (c) { return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]; }); }

  /* ---------- auto-open after N seconds on site ---------- */
  function armTimer() {
    if (!SHOW) return;
    var secs = cfg.POPUP_AFTER_SECONDS || 0;
    if (!secs) return;
    if (sessionStorage.getItem("yespyq_popup_shown")) return; // once per session
    setTimeout(function () {
      if (_paid || overlay) return;
      sessionStorage.setItem("yespyq_popup_shown", "1");
      openUnlock("timer");
    }, secs * 1000);
  }

  /* ---------- delegated clicks ---------- */
  document.addEventListener("click", function (e) {
    var ts = e.target.closest("[data-theme-set]");
    if (ts) {
      e.preventDefault();
      if (window.YQTheme) window.YQTheme.set(ts.dataset.themeSet);
      ts.parentNode.querySelectorAll(".at-opt").forEach(function (b) { b.classList.toggle("on", b === ts); });
      return;
    }
    var at = e.target.closest("[data-acct-toggle]");
    if (at) { e.preventDefault(); var m = at.parentNode.querySelector(".acct-menu"); if (m) m.hidden = !m.hidden; return; }
    var om = document.querySelector(".acct-menu:not([hidden])");
    if (om && !e.target.closest("#pay-acct")) om.hidden = true;
    if (e.target.closest("[data-unlock-close]") || (overlay && e.target === overlay)) { e.preventDefault(); closeUnlock(); return; }
    if (e.target.closest("[data-unlock-signin]")) { e.preventDefault(); signInWithGoogle(false); return; }
    if (e.target.closest("[data-unlock-buy]")) { e.preventDefault(); startCheckout(); return; }
    var u = e.target.closest("[data-unlock]");
    if (u) { e.preventDefault(); track("premium_click", { source: u.dataset.unlock || "cta" }); openUnlock(u.dataset.unlock || "cta"); return; }
    if (e.target.closest("[data-pay-signout]")) { e.preventDefault(); signOut(); return; }
  });

  /* ---------- boot ---------- */
  function boot() { renderChrome(); armTimer(); initSession(); track("page_view", { gated: GATE, paid: _paid }); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
