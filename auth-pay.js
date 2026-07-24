/* ============================================================
   YESPYQ — auth + payment layer (soft paywall), site-wide.
   Loaded on EVERY page (via theme.js). It:
     • injects the "👑 Premium" button into the header
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
  function backendReady() {
    return ph(cfg.SUPABASE_URL, "YOUR-PROJECT") && ph(cfg.SUPABASE_ANON_KEY, "YOUR_") &&
           ph(cfg.RAZORPAY_KEY_ID, "YOUR") && !!window;
  }
  var FUNCS = (cfg.FUNCTIONS_BASE || (cfg.SUPABASE_URL || "") + "/functions/v1").replace(/\/$/, "");
  var INTENT = "yespyq_pay_intent";

  var sb = null, _user = null, _paid = false;

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
      if (_user) refreshEntitlement().then(function () { renderChrome(); notify(); });
      else { _paid = false; renderChrome(); notify(); }
    });
    return sb;
  }
  async function ensureRzp() { if (!window.Razorpay) await loadScript("https://checkout.razorpay.com/v1/checkout.js"); }

  async function refreshEntitlement() {
    if (!_user || !sb) { _paid = false; return; }
    try {
      var r = await sb.from("entitlements").select("paid").eq("user_id", _user.id).maybeSingle();
      _paid = !!(r && r.data && r.data.paid);
    } catch (e) { _paid = false; }
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
  async function initSession() {
    if (!backendReady() || !hasStoredSession()) return;
    try {
      await ensureSb();
      var res = await sb.auth.getSession();
      var session = res && res.data && res.data.session;
      if (session) { _user = session.user; await refreshEntitlement(); renderChrome(); notify(); }
      if (_user && !_paid && localStorage.getItem(INTENT)) { localStorage.removeItem(INTENT); startCheckout(); }
    } catch (e) {}
  }

  /* ---------- auth ---------- */
  async function signInWithGoogle() {
    if (!backendReady()) { comingSoon(); return; }
    localStorage.setItem(INTENT, "1");
    await ensureSb();
    sb.auth.signInWithOAuth({ provider: "google", options: { redirectTo: location.origin + location.pathname } });
  }
  async function signOut() { try { if (sb) await sb.auth.signOut(); } catch (e) {} _user = null; _paid = false; renderChrome(); notify(); }

  /* ---------- payment ---------- */
  async function startCheckout() {
    if (!backendReady()) { comingSoon(); return; }
    if (!_user) { await signInWithGoogle(); return; }
    await ensureRzp();
    setBusy(true);
    var token = await accessToken(), order;
    try {
      var resp = await fetch(FUNCS + "/create-order", {
        method: "POST", headers: { "Content-Type": "application/json", "Authorization": "Bearer " + token }, body: "{}"
      });
      order = await resp.json();
      if (!resp.ok || !order.id) throw 0;
    } catch (e) { setBusy(false); alert("Could not start payment. Please try again."); return; }

    var rzp = new window.Razorpay({
      key: cfg.RAZORPAY_KEY_ID, order_id: order.id, amount: order.amount, currency: order.currency || "INR",
      name: "YESPYQ Premium", description: "Lifetime access — all PYQs & explanations",
      image: "https://yespyq.com/assets/favicon.svg", prefill: { email: _user.email || "" }, theme: { color: "#ea580c" },
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
      modal: { ondismiss: function () { setBusy(false); } }
    });
    rzp.on("payment.failed", function () { setBusy(false); alert("Payment failed or cancelled."); });
    setBusy(false); rzp.open();
  }
  function onPaid() { closeUnlock(); renderChrome(); notify(); showToast("🎉 Premium unlocked — enjoy full access!"); }
  function comingSoon() { showToast("💛 Premium is launching very soon — thanks for your interest!"); }

  /* ============================================================
     UI
     ============================================================ */
  var overlay = null;

  /* inject the Premium button into the header on every page */
  function injectHeaderButton() {
    var bar = document.querySelector(".site-header .header-inner");
    if (!bar || bar.querySelector("[data-unlock='header']")) return;
    var a = document.createElement("a");
    a.href = "#"; a.className = "btn btn-premium btn-sm"; a.setAttribute("data-unlock", "header");
    a.innerHTML = "👑 Premium";
    var cta = bar.querySelector(".btn-primary");
    if (cta) bar.insertBefore(a, cta); else bar.appendChild(a);
  }

  function renderChrome() {
    if (!SHOW) return;
    injectHeaderButton();
    // floating pill (hidden when paid)
    var pill = document.getElementById("pay-pill");
    if (_paid) { if (pill) pill.remove(); }
    else {
      if (!pill) {
        pill = document.createElement("button");
        pill.id = "pay-pill"; pill.className = "pay-pill"; pill.setAttribute("data-unlock", "float");
        document.body.appendChild(pill);
      }
      pill.innerHTML = '<span class="pp-star">✨</span> Go Premium <b>' + (cfg.PRICE_LABEL || "₹149") + '</b>';
    }
    // hide any Premium buttons for paid users
    if (_paid) document.querySelectorAll("[data-unlock='header']").forEach(function (el) { el.style.display = "none"; });
  }

  function featureList() {
    return [
      ["📚", "All 2,200+ UPSC PYQs", "Every subject & year, fully unlocked"],
      ["💡", "Detailed explanations", "The why behind every answer"],
      ["⚡", "Unlimited quiz mode", "Practice as much as you want"],
      ["🎯", "Subject & year filters", "Target exactly what you need"],
      ["♾️", "Lifetime access", "One-time payment, no subscription"],
      ["📈", "Track XP & streaks", "Stay motivated every day"]
    ].map(function (x) {
      return '<li><span class="uf-ic">' + x[0] + '</span><span class="uf-t"><b>' + x[1] + '</b><em>' + x[2] + '</em></span><span class="uf-ck">✓</span></li>';
    }).join("");
  }

  function openUnlock(context) {
    if (!SHOW || _paid || overlay) return;
    overlay = document.createElement("div");
    overlay.className = "unlock-overlay";
    var loggedIn = !!_user;
    var cta = loggedIn ? "Unlock everything · " + (cfg.PRICE_LABEL || "₹149") : "Continue with Google";
    var sub = loggedIn ? "One-time payment · instant lifetime access" : "Sign in, then pay " + (cfg.PRICE_LABEL || "₹149") + " once — instant access";
    overlay.innerHTML =
      '<div class="unlock-card" role="dialog" aria-modal="true">' +
        '<button class="unlock-x" data-unlock-close aria-label="Close">×</button>' +
        '<div class="unlock-banner"><span class="ub-shine"></span><span class="ub-crown">👑</span> YESPYQ PREMIUM</div>' +
        '<div class="unlock-main">' +
          '<div class="unlock-left">' +
            '<h2>Unlock everything you need to crack Prelims</h2>' +
            '<p class="unlock-tag">Join aspirants practising the complete PYQ bank — one place, one price.</p>' +
            '<ul class="unlock-feats">' + featureList() + '</ul>' +
          '</div>' +
          '<div class="unlock-right">' +
            '<div class="unlock-price"><span class="up-amt">' + (cfg.PRICE_LABEL || "₹149") + '</span><span class="up-note">one-time · lifetime</span></div>' +
            '<button class="unlock-cta" data-unlock-buy><span class="uc-glow"></span>' + escapeH(cta) + '</button>' +
            '<p class="unlock-sub">' + escapeH(sub) + '</p>' +
            '<div class="unlock-trust"><span>🔒 Secure via Razorpay</span><span>⚡ Instant access</span><span>♾️ No subscription</span></div>' +
            (loggedIn ? '' : '<p class="unlock-restore">Already purchased? <a href="#" data-unlock-buy>Sign in to restore</a></p>') +
          '</div>' +
        '</div>' +
      '</div>';
    document.body.appendChild(overlay);
    document.body.style.overflow = "hidden";
    requestAnimationFrame(function () { overlay.classList.add("in"); });
  }
  function closeUnlock() {
    if (!overlay) return;
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
    if (e.target.closest("[data-unlock-close]") || (overlay && e.target === overlay)) { e.preventDefault(); closeUnlock(); return; }
    if (e.target.closest("[data-unlock-buy]")) { e.preventDefault(); startCheckout(); return; }
    var u = e.target.closest("[data-unlock]");
    if (u) { e.preventDefault(); openUnlock(u.dataset.unlock || "cta"); return; }
    if (e.target.closest("[data-pay-signout]")) { e.preventDefault(); signOut(); return; }
  });

  /* ---------- boot ---------- */
  function boot() { renderChrome(); armTimer(); initSession(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
