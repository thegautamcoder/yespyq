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
  // auth (Supabase) and payment (Razorpay) readiness are independent:
  // sign-in can work before the Razorpay key is filled in.
  function authReady() { return ph(cfg.SUPABASE_URL, "YOUR-PROJECT") && ph(cfg.SUPABASE_ANON_KEY, "YOUR_"); }
  function backendReady() { return authReady() && ph(cfg.RAZORPAY_KEY_ID, "YOUR"); }
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
    if (!authReady() || !hasStoredSession()) return;
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
    if (!authReady()) { comingSoon(); return; }
    localStorage.setItem(INTENT, "1");
    await ensureSb();
    sb.auth.signInWithOAuth({ provider: "google", options: { redirectTo: location.origin + location.pathname } });
  }
  async function signOut() { try { if (sb) await sb.auth.signOut(); } catch (e) {} _user = null; _paid = false; renderChrome(); notify(); }

  /* ---------- email OTP fallback ---------- */
  var _otpEmail = "";
  function otpHint(t) { var h = overlay && overlay.querySelector("[data-otp-hint]"); if (h) h.textContent = t; }
  function toggleEmail() {
    var a = overlay && overlay.querySelector(".email-alt"), t = overlay && overlay.querySelector(".email-toggle");
    if (a) a.hidden = false; if (t) t.style.display = "none";
    var i = overlay && overlay.querySelector('[data-otp-step="1"] .email-in'); if (i) i.focus();
  }
  async function sendOtp() {
    if (!authReady()) { comingSoon(); return; }
    var el = overlay && overlay.querySelector('[data-otp-step="1"] .email-in');
    var email = el ? el.value.trim() : "";
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { otpHint("Enter a valid email address."); return; }
    _otpEmail = email; otpHint("Sending code…");
    try {
      await ensureSb();
      var r = await sb.auth.signInWithOtp({ email: email, options: { shouldCreateUser: true } });
      if (r.error) throw r.error;
      var s1 = overlay.querySelector('[data-otp-step="1"]'), s2 = overlay.querySelector('[data-otp-step="2"]');
      if (s1) s1.hidden = true; if (s2) s2.hidden = false;
      otpHint("Code sent to " + email + " — check your inbox.");
      var c = overlay.querySelector(".otp-in"); if (c) c.focus();
    } catch (e) { otpHint("Could not send code. Please try again."); }
  }
  async function verifyOtp() {
    var c = overlay && overlay.querySelector(".otp-in");
    var code = c ? c.value.trim() : "";
    if (!/^\d{4,8}$/.test(code)) { otpHint("Enter the code from your email."); return; }
    otpHint("Verifying…");
    try {
      await ensureSb();
      var r = await sb.auth.verifyOtp({ email: _otpEmail, token: code, type: "email" });
      if (r.error) throw r.error;
      _user = (r.data && r.data.user) || _user;
      await refreshEntitlement();
      if (_paid) { onPaid(); return; }
      otpHint(""); startCheckout();
    } catch (e) { otpHint("Invalid or expired code. Try again."); }
  }

  /* ---------- payment ---------- */
  async function startCheckout() {
    if (!authReady()) { comingSoon(); return; }
    if (!_user) { await signInWithGoogle(); return; }      // sign-in works even before Razorpay is set
    if (!backendReady()) { comingSoon(); return; }          // signed in, but payments not live yet
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
      image: "https://yespyq.com/assets/favicon.svg", prefill: { email: _user.email || "" }, theme: { color: "#6366f1" },
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

  /* Free-vs-Premium comparison — loss-framing converts better than bullets */
  function compareTable() {
    var rows = [
      ["All 2,237 UPSC PYQs (1995–2024)", "20 preview", "✓ All"],
      ["Detailed explanations", "Preview only", "✓ Every answer"],
      ["Quiz mode", "1 / day", "✓ Unlimited"],
      ["All 30 years · 7 subjects", "Limited", "✓ Everything"],
      ["Future question updates", "—", "✓ Free forever"]
    ].map(function (r) {
      return '<div class="cmp-row"><span class="cmp-f">' + r[0] + '</span><span class="cmp-no">' + r[1] + '</span><span class="cmp-yes">' + r[2] + '</span></div>';
    }).join("");
    return '<div class="cmp"><div class="cmp-row cmp-head"><span></span><span>Free</span><span class="cmp-pro">👑 Premium</span></div>' + rows + '</div>';
  }

  function openUnlock(context) {
    if (!SHOW || _paid || overlay) return;
    overlay = document.createElement("div");
    overlay.className = "unlock-overlay";
    var loggedIn = !!_user;
    var cta = "Get Lifetime Access →";
    var sub = loggedIn ? "One-time payment · unlocked in seconds" : "30 seconds: Google sign-in → pay " + (cfg.PRICE_LABEL || "₹149") + " → everything unlocks";
    overlay.innerHTML =
      '<div class="unlock-card" role="dialog" aria-modal="true">' +
        '<button class="unlock-x" data-unlock-close aria-label="Close">×</button>' +
        '<div class="unlock-banner"><span class="ub-shine"></span><span class="ub-crown">👑</span> YESPYQ PREMIUM <span class="ub-off">🔥 70% OFF — LAUNCH OFFER</span></div>' +
        '<div class="unlock-main">' +
          '<div class="unlock-left">' +
            '<h2>Every UPSC PYQ ever asked. Every explanation. One price.</h2>' +
            '<p class="unlock-tag">Toppers don’t guess what UPSC asks — they study what it already asked.</p>' +
            compareTable() +
            '<div class="unlock-stats"><span><b>2,237</b> PYQs</span><span><b>30</b> years</span><span><b>7</b> subjects</span></div>' +
          '</div>' +
          '<div class="unlock-right">' +
            '<div class="offer-chip">LAUNCH OFFER — ENDS SOON</div>' +
            '<div class="unlock-price"><span class="up-was">₹499</span><span class="up-amt">' + (cfg.PRICE_LABEL || "₹149") + '</span><span class="up-note">one-time · lifetime · no subscription</span><span class="up-math">less than one mock test 📝</span></div>' +
            '<button class="unlock-cta" data-unlock-buy><span class="uc-glow"></span>' + escapeH(cta) + '</button>' +
            '<p class="unlock-sub">' + escapeH(sub) + '</p>' +
            (loggedIn ? '' :
              '<button class="email-toggle" data-email-toggle>Prefer email? Use a code instead</button>' +
              '<div class="email-alt" hidden>' +
                '<div class="email-or">or continue with email</div>' +
                '<div class="email-step" data-otp-step="1">' +
                  '<input type="email" class="email-in" placeholder="you@email.com" autocomplete="email" />' +
                  '<button class="email-btn" data-otp-send>Send code</button>' +
                '</div>' +
                '<div class="email-step" data-otp-step="2" hidden>' +
                  '<input type="text" class="email-in otp-in" inputmode="numeric" maxlength="6" placeholder="6-digit code" />' +
                  '<button class="email-btn" data-otp-verify>Verify &amp; continue</button>' +
                '</div>' +
                '<div class="email-hint" data-otp-hint></div>' +
              '</div>') +
            '<div class="unlock-trust"><span>🔒 Secure via Razorpay</span><span>⚡ Instant access</span><span>♾️ No subscription</span></div>' +
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
    if (e.target.closest("[data-email-toggle]")) { e.preventDefault(); toggleEmail(); return; }
    if (e.target.closest("[data-otp-send]")) { e.preventDefault(); sendOtp(); return; }
    if (e.target.closest("[data-otp-verify]")) { e.preventDefault(); verifyOtp(); return; }
    var u = e.target.closest("[data-unlock]");
    if (u) { e.preventDefault(); openUnlock(u.dataset.unlock || "cta"); return; }
    if (e.target.closest("[data-pay-signout]")) { e.preventDefault(); signOut(); return; }
  });

  /* ---------- boot ---------- */
  function boot() { renderChrome(); armTimer(); initSession(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
