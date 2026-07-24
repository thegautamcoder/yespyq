-- YESPYQ paywall — run this once in Supabase → SQL Editor.
-- Stores who has paid. Users can read ONLY their own row; only the
-- Edge Functions (service role) can write, so a paid flag can't be forged.

create table if not exists public.entitlements (
  user_id              uuid primary key references auth.users(id) on delete cascade,
  paid                 boolean not null default false,
  amount               integer,
  currency             text default 'INR',
  razorpay_order_id    text,
  razorpay_payment_id  text,
  paid_at              timestamptz,
  created_at           timestamptz not null default now()
);

alter table public.entitlements enable row level security;

-- A signed-in user may read their own entitlement (to unlock content).
drop policy if exists entitlements_own_read on public.entitlements;
create policy entitlements_own_read
  on public.entitlements for select
  using (auth.uid() = user_id);

-- No insert/update/delete policies exist for normal users on purpose:
-- writes happen only via the Edge Functions using the service-role key.
