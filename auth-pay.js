/* ============================================================
   YESPYQ — auth + payment layer (soft paywall).
   Exposes window.PAY:
     PAY.isPaid()            -> boolean (true when ungated or user has paid)
     PAY.freeQuestions()     -> number
     PAY.freeQuizzesPerDay() -> number
     PAY.openUnlock(context) -> show the premium popup
     PAY.signOut()
   Fires window.onPayChange() whenever paid/login state changes so
   the app can re-render. Secret keys are NEVER here — the Razorpay
   secret lives only in the Supabase Edge Functions.
   ============================================================ */
(function () {
  "use strict";
  var cfg = window.PAY_CONFIG || {};
  var ENABLED = !!(cfg.ENABLED &&
    cfg.SUPABASE_URL && cfg.SUPABASE_URL.indexOf("YOUR-PROJECT") === -1 &&
    cfg.SUPABASE_ANON_KEY && cfg.SUPABASE_ANON_KEY.indexOf("YOUR_") === -1 &&
    window.supabase && typeof window.supabase.createClient === "function");

  var FUNCS = (cfg.FUNCTIONS_BASE || (cfg.SUPABASE_URL || "") + "/functions/v1").replace(/\/$/, "");
  var INTENT = "yespyq_pay_intent";

  var sb = null, _user = null, _paid = false, _ready = false;

  function notify() { try { if (typeof window.onPayChange === "function") window.onPayChange(); } catch (e) {} }

  var PAY = {
    isPaid: function () { return ENABLED ? _paid : true; },
    enabled: function () { return ENABLED; },
    user: function () { return _user; },
    freeQuestions: function () { return cfg.FREE_QUESTIONS || 20; },
    freeQuizzesPerDay: function () { return cfg.FREE_QUIZZES_PER_DAY || 1; },
    openUnlock: openUnlock,
    signOut: signOut,
    startCheckout: startCheckout
  };
  window.PAY = PAY;

  if (!ENABLED) { return; } // site behaves exactly as before

  /* ---------- init: restore session + entitlement ---------- */
  sb = window.supabase.createClient(cfg.SUPABASE_URL, cfg.SUPABASE_ANON_KEY);

  (async function init() {
    try {
      var res = await sb.auth.getSession();
      var session = res && res.data && res.data.session;
      if (session) { _user = session.user; await refreshEntitlement(); }
    } catch (e) {}
    _ready = true;
    renderChrome();
    notify();
    // auto-continue a purchase the user began before Google sign-in
    if (_user && !_paid && localStorage.getItem(INTENT)) {
      localStorage.removeItem(INTENT);
      startCheckout();
    }
    sb.auth.onAuthStateChange(function (_e, session) {
      _user = session ? session.user : null;
      if (_user) refreshEntitlement().then(function () { renderChrome(); notify(); });
      else { _paid = false; renderChrome(); notify(); }
    });
  })();

  async function refreshEntitlement() {
    if (!_user) { _paid = false; return; }
    try {
      var r = await sb.from("entitlements").select("paid").eq("user_id", _user.id).maybeSingle();
      _paid = !!(r && r.data && r.data.paid);
    } catch (e) { _paid = false; }
  }

  async function accessToken() {
    var r = await sb.auth.getSession();
    return r && r.data && r.data.session ? r.data.session.access_token : null;
  }

  /* ---------- auth ---------- */
  function signInWithGoogle() {
    localStorage.setItem(INTENT, "1"); // resume checkout after redirect back
    sb.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: location.origin + location.pathname }
    });
  }
  async function signOut() { try { await sb.auth.signOut(); } catch (e) {} _user = null; _paid = false; renderChrome(); notify(); }

  /* ---------- payment ---------- */
  async function startCheckout() {
    if (!_user) { signInWithGoogle(); return; }        // sign in first, then resume
    if (typeof window.Razorpay !== "function") { alert("Payment library still loading — please try again in a moment."); return; }
    setBusy(true);
    var token = await accessToken();
    var order;
    try {
      var resp = await fetch(FUNCS + "/create-order", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": "Bearer " + token },
        body: JSON.stringify({})
      });
      order = await resp.json();
      if (!resp.ok || !order.id) throw new Error(order.error || "order failed");
    } catch (e) { setBusy(false); alert("Could not start payment. Please try again."); return; }

    var rzp = new window.Razorpay({
      key: cfg.RAZORPAY_KEY_ID,
      order_id: order.id,
      amount: order.amount,
      currency: order.currency || "INR",
      name: "YESPYQ Premium",
      description: "Lifetime access — all PYQs & explanations",
      image: "https://yespyq.com/assets/favicon.svg",
      prefill: { email: _user.email || "" },
      theme: { color: "#2563eb" },
      handler: async function (r) {
        setBusy(true, "Verifying payment…");
        try {
          var vr = await fetch(FUNCS + "/verify-payment", {
            method: "POST",
            headers: { "Content-Type": "application/json", "Authorization": "Bearer " + token },
            body: JSON.stringify({
              razorpay_order_id: r.razorpay_order_id,
              razorpay_payment_id: r.razorpay_payment_id,
              razorpay_signature: r.razorpay_signature
            })
          });
          var vj = await vr.json();
          if (vr.ok && vj.paid) { _paid = true; onPaid(); }
          else throw new Error(vj.error || "verify failed");
        } catch (e) { alert("Payment received but verification failed. Contact teamyespyq@gmail.com with your payment id."); }
        setBusy(false);
      },
      modal: { ondismiss: function () { setBusy(false); } }
    });
    rzp.on("payment.failed", function () { setBusy(false); alert("Payment failed or was cancelled."); });
    setBusy(false);
    rzp.open();
  }

  function onPaid() {
    closeUnlock();
    renderChrome();
    notify();
    showToast("🎉 Premium unlocked — enjoy full access!");
  }

  /* ============================================================
     UI — floating pill, account chip, unlock popup
     ============================================================ */
  var overlay = null, busyMsg = null;

  function renderChrome() {
    if (!_ready) return;
    // floating "Go Premium" pill (hidden when paid)
    var pill = document.getElementById("pay-pill");
    if (_paid) { if (pill) pill.remove(); }
    else {
      if (!pill) {
        pill = document.createElement("button");
        pill.id = "pay-pill";
        pill.className = "pay-pill";
        pill.setAttribute("data-unlock", "float");
        document.body.appendChild(pill);
      }
      pill.innerHTML = '<span class="pp-star">✨</span> Go Premium <b>' + (cfg.PRICE_LABEL || "₹149") + '</b>';
    }
    // reflect paid state on any header unlock buttons
    document.querySelectorAll("[data-unlock]").forEach(function (el) {
      if (el.id === "pay-pill") return;
      el.classList.toggle("is-paid", _paid);
      if (_paid && el.dataset.hideWhenPaid !== "0") el.style.display = "none";
    });
  }

  function featureList() {
    var items = [
      ["📚", "All 2,200+ UPSC PYQs", "Every subject, every year — fully unlocked"],
      ["💡", "Detailed explanations", "The why behind every answer"],
      ["⚡", "Unlimited quiz mode", "Practice as much as you want, daily"],
      ["🎯", "Subject & year filters", "Target exactly what you need"],
      ["♾️", "Lifetime access", "One-time payment — no subscription"]
    ];
    return items.map(function (x) {
      return '<li><span class="uf-ic">' + x[0] + '</span><span class="uf-t"><b>' + x[1] + '</b><em>' + x[2] + '</em></span><span class="uf-ck">✓</span></li>';
    }).join("");
  }

  function openUnlock(context) {
    if (_paid) return;
    if (overlay) { closeUnlock(); }
    overlay = document.createElement("div");
    overlay.className = "unlock-overlay";
    var loggedIn = !!_user;
    var ctaLabel = loggedIn
      ? "Unlock everything · " + (cfg.PRICE_LABEL || "₹149")
      : "Continue with Google";
    var sub = loggedIn
      ? "One-time payment · Instant lifetime access"
      : "Sign in, then pay " + (cfg.PRICE_LABEL || "₹149") + " once — instant access";
    overlay.innerHTML =
      '<div class="unlock-card" role="dialog" aria-modal="true">' +
        '<button class="unlock-x" data-unlock-close aria-label="Close">×</button>' +
        '<div class="unlock-shine"></div>' +
        '<div class="unlock-head">' +
          '<div class="unlock-crown">👑</div>' +
          '<h2>Unlock YESPYQ Premium</h2>' +
          '<p class="unlock-tag">Everything you need to crack Prelims — in one place.</p>' +
        '</div>' +
        '<ul class="unlock-feats">' + featureList() + '</ul>' +
        '<div class="unlock-price"><span class="up-amt">' + (cfg.PRICE_LABEL || "₹149") + '</span><span class="up-note">one-time · lifetime</span></div>' +
        '<button class="unlock-cta" data-unlock-buy><span class="uc-glow"></span>' + escapeH(ctaLabel) + '</button>' +
        '<p class="unlock-sub">' + escapeH(sub) + '</p>' +
        '<div class="unlock-trust"><span>🔒 Secure via Razorpay</span><span>⚡ Instant access</span><span>♾️ No subscription</span></div>' +
        (loggedIn ? '' : '<p class="unlock-restore">Already purchased? <a href="#" data-unlock-buy>Sign in to restore</a></p>') +
      '</div>';
    document.body.appendChild(overlay);
    document.body.style.overflow = "hidden";
    requestAnimationFrame(function () { overlay.classList.add("in"); });
  }

  function closeUnlock() {
    if (!overlay) return;
    overlay.classList.remove("in");
    var o = overlay; overlay = null;
    document.body.style.overflow = "";
    setTimeout(function () { if (o && o.parentNode) o.parentNode.removeChild(o); }, 200);
  }

  function setBusy(on, msg) {
    var btn = overlay && overlay.querySelector(".unlock-cta");
    if (btn) {
      btn.disabled = !!on;
      btn.classList.toggle("busy", !!on);
      if (on && msg) { btn.dataset.prev = btn.dataset.prev || btn.textContent; btn.textContent = msg; }
      else if (!on && btn.dataset.prev) { btn.textContent = btn.dataset.prev; delete btn.dataset.prev; }
    }
  }

  function showToast(t) {
    var el = document.createElement("div");
    el.className = "pay-toast"; el.textContent = t;
    document.body.appendChild(el);
    requestAnimationFrame(function () { el.classList.add("in"); });
    setTimeout(function () { el.classList.remove("in"); setTimeout(function () { el.remove(); }, 300); }, 3200);
  }

  function escapeH(s) { return String(s).replace(/[&<>"]/g, function (c) { return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]; }); }

  /* ---------- delegated clicks ---------- */
  document.addEventListener("click", function (e) {
    if (e.target.closest("[data-unlock-close]") || (overlay && e.target === overlay)) { e.preventDefault(); closeUnlock(); return; }
    if (e.target.closest("[data-unlock-buy]")) { e.preventDefault(); startCheckout(); return; }
    var u = e.target.closest("[data-unlock]");
    if (u) { e.preventDefault(); openUnlock(u.dataset.unlock || "cta"); return; }
    if (e.target.closest("[data-pay-signout]")) { e.preventDefault(); signOut(); return; }
  });
})();
