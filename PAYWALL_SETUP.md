# YESPYQ Paywall — Setup Guide (₹149 lifetime unlock)

Everything is built and committed. The paywall is **OFF** until you complete the
steps below and flip one switch. While off, the live site behaves exactly as before.

**Golden rule:** your Razorpay **key_secret** only ever goes into Supabase (step 4).
It must NEVER be put in `pay-config.js` or any file in this repo.

---

## 0. Rotate the leaked secret first ⚠️
The `key_secret` in `~/Downloads/rzp-key.csv` was exposed in plaintext.
Razorpay Dashboard → Settings → API Keys → **Regenerate**. Use the new secret below.

## 1. Create a Supabase project
1. Go to https://supabase.com → new project (free tier is fine).
2. Project Settings → **API** → copy **Project URL** and the **anon public** key.

## 2. Enable Google sign-in
1. Supabase → Authentication → Providers → **Google** → enable.
2. It shows a **Callback URL** — copy it.
3. Google Cloud Console → APIs & Services → Credentials → **OAuth client ID** (Web):
   - Authorized redirect URI = the Supabase callback URL from step 2.
   - Authorized JavaScript origin = `https://yespyq.com`
   - Copy the **Client ID** + **Client secret** back into Supabase's Google provider.
4. Supabase → Authentication → URL Configuration → add `https://yespyq.com` to
   **Site URL** and **Redirect URLs**.

## 3. Create the database table
Supabase → SQL Editor → paste and run [`supabase/schema.sql`](supabase/schema.sql).

## 4. Set the server secrets (Razorpay secret lives ONLY here)
Install the CLI (`npm i -g supabase`), then:
```bash
cd /Users/pw/yespyq-deploy
supabase login
supabase link --project-ref YOUR_PROJECT_REF     # from the project URL
supabase secrets set \
  RAZORPAY_KEY_ID=rzp_test_xxxxxxxx \
  RAZORPAY_KEY_SECRET=YOUR_NEW_SECRET \
  PRICE_PAISE=14900 \
  PLAN_DAYS=365
```
(SUPABASE_URL / SUPABASE_ANON_KEY / SUPABASE_SERVICE_ROLE_KEY are injected by Supabase automatically.)

## 5. Deploy the two Edge Functions
```bash
supabase functions deploy create-order   --no-verify-jwt
supabase functions deploy verify-payment --no-verify-jwt
```

## 6. Fill the public config
Edit [`pay-config.js`](pay-config.js):
- `SUPABASE_URL`, `SUPABASE_ANON_KEY` → from step 1
- `RAZORPAY_KEY_ID` → your **test** key first (`rzp_test_...`)
- leave `ENABLED: false` for now

## 7. Test with fake money
Serve locally (`python3 -m http.server --directory /Users/pw/yespyq-deploy 4317`),
temporarily set `ENABLED: true`, open http://localhost:4317, and:
- browse past 20 questions → lock strip appears
- click **Premium** / the floating pill → popup → **Continue with Google** → sign in
- pay with a Razorpay **test card** (`4111 1111 1111 1111`, any future expiry/CVV)
- content unlocks, "Premium ✓" state sticks on reload

## 8. Go live
1. In `pay-config.js`: set `RAZORPAY_KEY_ID` to your **live** key `rzp_live_THPWiyqKLDnWYH`
   (or the regenerated one) and set `ENABLED: true`.
2. In Supabase secrets: set the **live** `RAZORPAY_KEY_ID` + **live** `RAZORPAY_KEY_SECRET`.
3. Commit + push to the deploy repo:
   ```bash
   gh auth switch --user thegautamcoder
   git add -A && git commit -m "Enable ₹149 premium paywall" && git push
   gh auth switch --user gautamproduct
   ```

---

## What's gated (soft paywall)
| Area | Free | Paid |
|---|---|---|
| Browse questions | first **20** per view | all ~2,200 |
| Explanations | on the free questions | all |
| Quiz mode | **1 / day** | unlimited |
| `/pyq/q/*` SEO pages | fully public (unchanged, protects SEO) | — |

Tune the free limits in `pay-config.js` (`FREE_QUESTIONS`, `FREE_QUIZZES_PER_DAY`).

## ⚠️ Copy that now contradicts a paywall (fix before/after going live)
The homepage still advertises **"completely free, no login."** Update these so you
don't mislead users or trip Google's policy checks:
- `index.html` meta description + OG/Twitter description ("Free … no login")
- The FAQ JSON-LD answer "Is YESPYQ free to use? Yes … completely free, no login required"
- Any "free" claims on `/about/`, blog, subject pages

## How the money flow stays safe
- Browser only ever holds the **public** `key_id` + anon key.
- `create-order` and `verify-payment` run on Supabase and are the only holders of the secret.
- `paid=true` is written **only** after the server verifies Razorpay's signature, and only
  via the service role — a user cannot forge it from the browser (RLS blocks writes).
