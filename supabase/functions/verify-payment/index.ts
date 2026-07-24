// YESPYQ — verify-payment Edge Function.
// Verifies the Razorpay signature server-side (HMAC-SHA256 of
// "order_id|payment_id" with the SECRET). Only on a valid signature does it
// write paid=true for the signed-in user, using the service-role key so the
// flag can't be forged from the browser.
//
// Deploy:  supabase functions deploy verify-payment --no-verify-jwt
// Secrets (shared with create-order): RAZORPAY_KEY_SECRET
//          plus SUPABASE_SERVICE_ROLE_KEY is injected automatically.

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return json({ error: "method not allowed" }, 405);

  const auth = req.headers.get("Authorization") || "";
  const url = Deno.env.get("SUPABASE_URL")!;

  // Who is calling (from their JWT)?
  const asUser = createClient(url, Deno.env.get("SUPABASE_ANON_KEY")!, {
    global: { headers: { Authorization: auth } },
  });
  const { data: { user }, error: uErr } = await asUser.auth.getUser();
  if (uErr || !user) return json({ error: "not authenticated" }, 401);

  const { razorpay_order_id, razorpay_payment_id, razorpay_signature } = await req.json();
  if (!razorpay_order_id || !razorpay_payment_id || !razorpay_signature) {
    return json({ error: "missing fields" }, 400);
  }

  // Verify signature = HMAC_SHA256(order_id + "|" + payment_id, key_secret).
  const secret = Deno.env.get("RAZORPAY_KEY_SECRET")!;
  const expected = await hmacHex(secret, `${razorpay_order_id}|${razorpay_payment_id}`);
  if (!timingSafeEqual(expected, razorpay_signature)) {
    return json({ error: "invalid signature" }, 400);
  }

  // Signature is genuine → record the entitlement with the service role.
  const admin = createClient(url, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
  const amount = parseInt(Deno.env.get("PRICE_PAISE") || "14900", 10);
  const { error: wErr } = await admin.from("entitlements").upsert({
    user_id: user.id,
    paid: true,
    amount,
    currency: "INR",
    razorpay_order_id,
    razorpay_payment_id,
    paid_at: new Date().toISOString(),
  }, { onConflict: "user_id" });
  if (wErr) return json({ error: "could not save entitlement" }, 500);

  return json({ paid: true });
});

async function hmacHex(secret: string, msg: string): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"],
  );
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(msg));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function timingSafeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let out = 0;
  for (let i = 0; i < a.length; i++) out |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return out === 0;
}

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...cors, "Content-Type": "application/json" },
  });
}
