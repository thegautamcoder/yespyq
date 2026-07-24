/* ============================================================
   YESPYQ paywall — PUBLIC config (safe to commit).
   Nothing secret here. The Razorpay SECRET lives ONLY in
   Supabase (see PAYWALL_SETUP.md). Fill the 4 values below,
   then set ENABLED:true to switch the paywall on for everyone.
   ============================================================ */
window.PAY_CONFIG = {
  // Master switch. While false, the whole site behaves exactly
  // as before (no gate, no popups). Flip to true once Supabase
  // + Razorpay below are configured and tested.
  ENABLED: false,

  // From Supabase → Project Settings → API  (both are public/safe)
  SUPABASE_URL: "https://YOUR-PROJECT.supabase.co",
  SUPABASE_ANON_KEY: "YOUR_SUPABASE_ANON_KEY",

  // Razorpay key_id ONLY (public). Use a TEST key first
  // (rzp_test_...), then swap to your LIVE key rzp_live_THPWiyqKLDnWYH.
  // The key_secret must NEVER appear here — it stays in Supabase.
  RAZORPAY_KEY_ID: "rzp_test_YOUR_TEST_KEY",

  // Price + free-preview limits
  PRICE_PAISE: 14900,          // ₹149.00
  PRICE_LABEL: "₹149",
  FREE_QUESTIONS: 20,          // questions a free user can browse per view
  FREE_QUIZZES_PER_DAY: 1,     // free quizzes per day

  // Optional: override if you use a custom functions domain.
  // Defaults to SUPABASE_URL + "/functions/v1".
  FUNCTIONS_BASE: ""
};
