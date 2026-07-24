/* ============================================================
   YESPYQ paywall — PUBLIC config (safe to commit). No secrets here.
   The Razorpay SECRET lives ONLY in Supabase (see PAYWALL_SETUP.md).
   ============================================================ */
window.PAY_CONFIG = {
  /* ---- display: the shiny Premium button, popup & auto-popup ---- */
  // Show the Premium button (all pages), the unlock popup, the floating
  // pill and the "spent N seconds" auto-popup. Safe with no backend —
  // if payments aren't wired yet the popup shows a "launching soon" note.
  SHOW_POPUP: true,
  POPUP_AFTER_SECONDS: 120,     // auto-open the popup after this long on site (0 = off)

  /* ---- enforcement: actually require ₹149 to see everything ---- */
  // Turn ON only once Supabase + Razorpay below are live & tested.
  // While false, the whole site stays fully usable (no content locked).
  GATE_CONTENT: true,
  FREE_QUESTIONS: 20,           // questions a free user can browse per view
  FREE_QUIZZES_PER_DAY: 1,      // free quizzes per day

  /* ---- backend (fill to make payments actually work) ---- */
  // From Supabase → Project Settings → API (both public/safe)
  SUPABASE_URL: "https://jcfyoovojzkxzqrzlcpz.supabase.co",
  SUPABASE_ANON_KEY: "sb_publishable_uVIZ60AYMFj3hdnhPYp4lw_AtMJLRNS",
  // Razorpay key_id ONLY (public). Test key first (rzp_test_...),
  // then live rzp_live_THPWiyqKLDnWYH. The SECRET never goes here.
  RAZORPAY_KEY_ID: "rzp_live_THPWiyqKLDnWYH",

  PRICE_PAISE: 14900,           // ₹149.00
  PRICE_LABEL: "₹149",
  PLAN_DAYS: 365,               // plan validity (client display; server enforces via PLAN_DAYS secret)
  FUNCTIONS_BASE: ""            // defaults to SUPABASE_URL + "/functions/v1"
};
