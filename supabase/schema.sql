-- YESPYQ paywall + analytics — run this in Supabase → SQL Editor.
-- Safe to re-run (idempotent). Users can only ever read/write their OWN rows;
-- the paid flag is writable only by the Edge Functions (service role).

/* ============================================================
   1. ENTITLEMENTS — who paid, how much, until when
   ============================================================ */
create table if not exists public.entitlements (
  user_id              uuid primary key references auth.users(id) on delete cascade,
  email                text,
  paid                 boolean not null default false,
  amount               integer,                -- in paise (14900 = ₹149)
  currency             text default 'INR',
  razorpay_order_id    text,
  razorpay_payment_id  text,
  paid_at              timestamptz,            -- most recent payment
  first_paid_at        timestamptz,            -- their very first payment
  expires_at           timestamptz,            -- access valid until this moment
  purchase_count       integer not null default 0,   -- 1 = new, 2+ = renewals
  created_at           timestamptz not null default now()
);
-- add columns if the table already existed from an earlier version
alter table public.entitlements add column if not exists email          text;
alter table public.entitlements add column if not exists expires_at     timestamptz;
alter table public.entitlements add column if not exists first_paid_at  timestamptz;
alter table public.entitlements add column if not exists purchase_count integer not null default 0;

alter table public.entitlements enable row level security;
drop policy if exists entitlements_own_read on public.entitlements;
create policy entitlements_own_read on public.entitlements
  for select using (auth.uid() = user_id);

/* ============================================================
   2. USER PROFILES — rollup: logins, time spent, last seen
   ============================================================ */
create table if not exists public.user_profiles (
  user_id        uuid primary key references auth.users(id) on delete cascade,
  email          text,
  full_name      text,
  first_seen_at  timestamptz not null default now(),
  last_login_at  timestamptz,
  last_seen_at   timestamptz,
  login_count    integer not null default 0,
  total_seconds  bigint  not null default 0,   -- cumulative time on site
  created_at     timestamptz not null default now()
);
alter table public.user_profiles enable row level security;
drop policy if exists profiles_own_read on public.user_profiles;
create policy profiles_own_read on public.user_profiles
  for select using (auth.uid() = user_id);

/* ============================================================
   3. LOGIN EVENTS — one row per sign-in (for cohort analysis)
   ============================================================ */
create table if not exists public.user_logins (
  id            bigserial primary key,
  user_id       uuid references auth.users(id) on delete cascade,
  email         text,
  logged_in_at  timestamptz not null default now(),
  user_agent    text
);
create index if not exists user_logins_user_idx on public.user_logins(user_id, logged_in_at desc);
alter table public.user_logins enable row level security;
drop policy if exists logins_own_read on public.user_logins;
create policy logins_own_read on public.user_logins
  for select using (auth.uid() = user_id);

/* ============================================================
   4. RPCs — the only way the browser can write analytics.
      SECURITY DEFINER + auth.uid() means a user can never
      write a row for somebody else, or fake a paid flag.
   ============================================================ */
create or replace function public.record_login(p_user_agent text default null)
returns void language plpgsql security definer set search_path = public as $$
declare u uuid := auth.uid(); e text;
begin
  if u is null then return; end if;
  select email into e from auth.users where id = u;

  insert into public.user_logins(user_id, email, user_agent) values (u, e, p_user_agent);

  insert into public.user_profiles(user_id, email, last_login_at, last_seen_at, login_count)
  values (u, e, now(), now(), 1)
  on conflict (user_id) do update
    set login_count   = public.user_profiles.login_count + 1,
        last_login_at = now(),
        last_seen_at  = now(),
        email         = excluded.email;

  update public.entitlements set email = e where user_id = u and email is distinct from e;
end $$;

create or replace function public.record_activity(p_seconds integer)
returns void language plpgsql security definer set search_path = public as $$
declare u uuid := auth.uid(); e text;
begin
  if u is null or p_seconds is null or p_seconds <= 0 or p_seconds > 3600 then return; end if;
  select email into e from auth.users where id = u;

  insert into public.user_profiles(user_id, email, total_seconds, last_seen_at)
  values (u, e, p_seconds, now())
  on conflict (user_id) do update
    set total_seconds = public.user_profiles.total_seconds + p_seconds,
        last_seen_at  = now();
end $$;

grant execute on function public.record_login(text)     to authenticated;
grant execute on function public.record_activity(integer) to authenticated;

/* ============================================================
   5. HANDY VIEW — your paying customers at a glance
      (read it in Table Editor / SQL Editor)
   ============================================================ */
create or replace view public.paid_customers as
select
  e.email,
  e.amount / 100.0                          as amount_rupees,
  e.paid_at,
  e.expires_at,
  greatest(0, date_part('day', e.expires_at - now()))::int as days_left,
  (e.expires_at <= now())                   as is_expired,
  e.purchase_count,
  p.login_count,
  p.last_login_at,
  round(p.total_seconds / 60.0, 1)          as minutes_on_site
from public.entitlements e
left join public.user_profiles p on p.user_id = e.user_id
where e.paid
order by e.paid_at desc;
