// YESPYQ — create-order Edge Function.
// Creates a ₹149 Razorpay order server-side. Requires a signed-in user
// (Supabase JWT in the Authorization header). Uses the Razorpay SECRET
// which is stored as a Supabase secret and NEVER sent to the browser.
//
// Deploy:  supabase functions deploy create-order --no-verify-jwt
// Secrets: supabase secrets set RAZORPAY_KEY_ID=... RAZORPAY_KEY_SECRET=... \
//                               PRICE_PAISE=14900

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return json({ error: "method not allowed" }, 405);

  // Identify the caller from their Supabase JWT.
  const auth = req.headers.get("Authorization") || "";
  const supa = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_ANON_KEY")!,
    { global: { headers: { Authorization: auth } } },
  );
  const { data: { user }, error } = await supa.auth.getUser();
  if (error || !user) return json({ error: "not authenticated" }, 401);

  const keyId = Deno.env.get("RAZORPAY_KEY_ID")!;
  const keySecret = Deno.env.get("RAZORPAY_KEY_SECRET")!;
  const amount = parseInt(Deno.env.get("PRICE_PAISE") || "14900", 10);

  // Create the order via Razorpay Orders API (Basic auth = key_id:key_secret).
  const res = await fetch("https://api.razorpay.com/v1/orders", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Basic " + btoa(`${keyId}:${keySecret}`),
    },
    body: JSON.stringify({
      amount,
      currency: "INR",
      receipt: `yespyq_${user.id.slice(0, 8)}_${Date.now()}`,
      notes: { user_id: user.id, email: user.email ?? "" },
    }),
  });

  const order = await res.json();
  if (!res.ok) return json({ error: order?.error?.description || "razorpay error" }, 502);

  return json({ id: order.id, amount: order.amount, currency: order.currency });
});

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...cors, "Content-Type": "application/json" },
  });
}
