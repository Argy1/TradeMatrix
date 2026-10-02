-- TradeMatrix AI — initial schema (Created by Argy)
-- All timestamps are UTC (timestamptz). Backend connects with a privileged role (bypasses RLS);
-- RLS protects direct client access (Supabase JS / Flutter SDK).

-- ============ Reference data ============
create table public.assets (
  id              smallint generated always as identity primary key,
  symbol          text not null unique,          -- 'BTC'
  name            text not null,                 -- 'Bitcoin'
  exchange_symbol text not null,                 -- 'BTCUSDT'
  active          boolean not null default true,
  created_at      timestamptz not null default now()
);

insert into public.assets (symbol, name, exchange_symbol) values
  ('BTC', 'Bitcoin',  'BTCUSDT'),
  ('ETH', 'Ethereum', 'ETHUSDT'),
  ('SOL', 'Solana',   'SOLUSDT'),
  ('BNB', 'BNB',      'BNBUSDT'),
  ('XRP', 'XRP',      'XRPUSDT');

-- ============ Market data ============
create table public.candles (
  asset_id   smallint not null references public.assets(id),
  timeframe  text not null check (timeframe in ('1h','4h','1d')),
  open_time  timestamptz not null,
  open       numeric not null,
  high       numeric not null,
  low        numeric not null,
  close      numeric not null,
  volume     numeric not null check (volume >= 0),
  primary key (asset_id, timeframe, open_time),
  check (high >= greatest(open, close) and low <= least(open, close))
);

-- ============ News and sentiment ============
create table public.news_items (
  id            bigint generated always as identity primary key,
  source        text not null,
  title         text not null,
  url           text not null unique,
  title_hash    text not null,                   -- normalized-title hash for dedupe
  published_at  timestamptz not null,
  asset_symbols text[] not null default '{}',    -- keyword-tagged, e.g. {BTC,ETH}
  fetched_at    timestamptz not null default now()
);
create index news_items_published_idx on public.news_items (published_at desc);
create index news_items_title_hash_idx on public.news_items (title_hash);

create table public.sentiments (
  news_id    bigint primary key references public.news_items(id) on delete cascade,
  assets     text[] not null default '{}',       -- symbols Gemini says are affected
  score      real not null check (score between -1 and 1),
  confidence real not null check (confidence between 0 and 1),
  event_type text not null check (event_type in
             ('regulation','hack','listing','etf','macro','partnership','technical','market','other')),
  reason     text not null,
  model      text not null,                      -- Gemini model used
  prompt_version text not null,
  created_at timestamptz not null default now()
);

-- ============ Models and predictions ============
create table public.model_versions (
  id            integer generated always as identity primary key,
  asset_id      smallint not null references public.assets(id),
  timeframe     text not null check (timeframe in ('1h','4h','1d')),
  trained_at    timestamptz not null default now(),
  train_start   timestamptz not null,
  train_end     timestamptz not null,
  metrics       jsonb not null default '{}',      -- walk-forward metrics + baselines
  artifact_path text not null,                    -- Supabase Storage path in bucket 'models'
  is_active     boolean not null default false,
  status        text not null default 'ok' check (status in ('ok','degraded'))
);
-- at most one active model per asset + timeframe
create unique index model_versions_one_active_idx
  on public.model_versions (asset_id, timeframe) where is_active;

create table public.predictions (
  id               bigint generated always as identity primary key,
  asset_id         smallint not null references public.assets(id),
  timeframe        text not null check (timeframe in ('1h','4h','1d')),
  base_open_time   timestamptz not null,          -- open time of the last CLOSED candle used
  target_open_time timestamptz not null,          -- open time of the candle being predicted
  base_close       numeric not null,
  p_ml             real not null check (p_ml between 0 and 1),   -- calibrated model probability
  p_up             real not null check (p_up between 0 and 1),   -- final (after sentiment blend)
  label            text not null check (label in ('up','down','neutral')),
  sentiment_agg    real not null default 0,
  sentiment_k      real not null default 0,       -- k used for this row (0 = shadow mode)
  model_version_id integer not null references public.model_versions(id),
  features         jsonb not null,                -- feature snapshot for audit
  reasons          jsonb not null default '[]',   -- up to 3 template-based reasons
  created_at       timestamptz not null default now(),
  unique (asset_id, timeframe, target_open_time)
);
create index predictions_lookup_idx on public.predictions (asset_id, timeframe, created_at desc);

create table public.prediction_outcomes (
  prediction_id    bigint primary key references public.predictions(id) on delete cascade,
  target_close     numeric not null,
  actual_direction text not null check (actual_direction in ('up','down')),  -- flat counts as 'down'
  correct          boolean,                        -- null when the label was 'neutral'
  return_pct       real not null,
  resolved_at      timestamptz not null default now()
);

-- ============ User data ============
create table public.watchlists (
  user_id    uuid not null references auth.users(id) on delete cascade,
  asset_id   smallint not null references public.assets(id),
  created_at timestamptz not null default now(),
  primary key (user_id, asset_id)
);

create table public.alerts (
  id                uuid primary key default gen_random_uuid(),
  user_id           uuid not null references auth.users(id) on delete cascade,
  asset_id          smallint not null references public.assets(id),
  timeframe         text check (timeframe in ('1h','4h','1d')),  -- null for price alerts
  type              text not null check (type in
                    ('signal_change','prob_above','prob_below','price_above','price_below')),
  threshold         numeric,                         -- probability (0-1) or price; null for signal_change
  cooldown_minutes  integer not null default 60 check (cooldown_minutes >= 0),
  active            boolean not null default true,
  last_triggered_at timestamptz,
  created_at        timestamptz not null default now()
);
create index alerts_user_idx on public.alerts (user_id);
create index alerts_active_idx on public.alerts (asset_id, type) where active;

create table public.notifications (
  id         bigint generated always as identity primary key,
  user_id    uuid not null references auth.users(id) on delete cascade,
  alert_id   uuid references public.alerts(id) on delete set null,
  title      text not null,
  body       text not null,
  data       jsonb not null default '{}',
  created_at timestamptz not null default now(),
  read_at    timestamptz
);
create index notifications_user_idx on public.notifications (user_id, created_at desc);

create table public.device_tokens (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid not null references auth.users(id) on delete cascade,
  fcm_token    text not null unique,
  platform     text not null check (platform in ('android','ios','web')),
  created_at   timestamptz not null default now(),
  last_seen_at timestamptz not null default now()
);
create index device_tokens_user_idx on public.device_tokens (user_id);

-- ============ Operations ============
create table public.worker_heartbeat (
  job_name        text primary key,
  last_run_at     timestamptz,
  last_success_at timestamptz,
  last_error      text
);

-- ============ Row Level Security ============
alter table public.assets              enable row level security;
alter table public.candles             enable row level security;
alter table public.news_items          enable row level security;
alter table public.sentiments          enable row level security;
alter table public.model_versions      enable row level security;
alter table public.predictions         enable row level security;
alter table public.prediction_outcomes enable row level security;
alter table public.watchlists          enable row level security;
alter table public.alerts              enable row level security;
alter table public.notifications       enable row level security;
alter table public.device_tokens       enable row level security;
alter table public.worker_heartbeat    enable row level security;

-- Public read-only market data (no write policies => only the backend can write)
create policy "public read assets"      on public.assets              for select to anon, authenticated using (true);
create policy "public read candles"     on public.candles             for select to anon, authenticated using (true);
create policy "public read news"        on public.news_items          for select to anon, authenticated using (true);
create policy "public read sentiments"  on public.sentiments          for select to anon, authenticated using (true);
create policy "public read predictions" on public.predictions         for select to anon, authenticated using (true);
create policy "public read outcomes"    on public.prediction_outcomes for select to anon, authenticated using (true);
-- model_versions and worker_heartbeat: no policies => not readable by clients (backend only)

-- Per-user data
create policy "own watchlist" on public.watchlists for all to authenticated
  using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "own alerts" on public.alerts for all to authenticated
  using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "own devices" on public.device_tokens for all to authenticated
  using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "read own notifications" on public.notifications for select to authenticated
  using ((select auth.uid()) = user_id);
create policy "mark own notifications read" on public.notifications for update to authenticated
  using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
-- notifications are inserted by the backend only (no insert policy for clients)
