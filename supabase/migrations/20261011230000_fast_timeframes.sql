-- Fast candle sizes (Phase 5b, scope change approved by Argy on 2026-10-11):
-- 1m, 3m, 5m, 15m and 30m next to 1h, 4h and 1d. Binance has no 10m candle, so 15m takes
-- its place.
--
-- This migration only widens and adds. The code that runs today keeps working with it, so it
-- is applied before the new worker and API are deployed.

-- ALTER TABLE needs the table to itself for a moment. If another query is in the way, a
-- waiting ALTER makes every later query on that table wait behind it. So give up after
-- 5 seconds instead: nothing is changed, and the migration can simply be run again.
set local lock_timeout = '5s';

-- ---------------------------------------------------------------------------------------
-- 1. Allow the new sizes.
-- "not valid" means: check every NEW row from now on, but do not read the existing rows yet.
-- Reading 1.1 million candles would hold the table lock for the whole scan. The existing
-- rows are checked by the next migration, which needs only a light lock.
-- ---------------------------------------------------------------------------------------
alter table public.candles
  drop constraint candles_timeframe_check,
  add constraint candles_timeframe_check
    check (timeframe in ('1m','3m','5m','15m','30m','1h','4h','1d')) not valid;

alter table public.model_versions
  drop constraint model_versions_timeframe_check,
  add constraint model_versions_timeframe_check
    check (timeframe in ('1m','3m','5m','15m','30m','1h','4h','1d')) not valid;

alter table public.predictions
  drop constraint predictions_timeframe_check,
  add constraint predictions_timeframe_check
    check (timeframe in ('1m','3m','5m','15m','30m','1h','4h','1d')) not valid;

alter table public.alerts
  drop constraint alerts_timeframe_check,
  add constraint alerts_timeframe_check
    check (timeframe in ('1m','3m','5m','15m','30m','1h','4h','1d')) not valid;

-- ---------------------------------------------------------------------------------------
-- 2. A third result: 'flat'.
-- On 1h candles a close at exactly the previous close is rare and counts as 'down' (docs/04).
-- On one-minute candles of a low-priced coin it can be half of all candles. Counted as 'down',
-- a model would learn to say Down all day and look right without knowing any direction. So on
-- the fast sizes a flat candle is 'flat': no result, correct = null, like a Neutral call.
-- The slow sizes keep their rule.
-- ---------------------------------------------------------------------------------------
alter table public.prediction_outcomes
  drop constraint prediction_outcomes_actual_direction_check,
  add constraint prediction_outcomes_actual_direction_check
    check (actual_direction in ('up','down','flat')) not valid;

comment on column public.prediction_outcomes.actual_direction is
  'up, down, or flat. flat (close equal to the base close) exists only on sizes under 1h and has no result; on 1h, 4h and 1d a flat close counts as down.';
comment on column public.prediction_outcomes.correct is
  'null when the label was neutral or the result was flat';

-- ---------------------------------------------------------------------------------------
-- 3. Order flow on candles (used by the fast models' features).
-- trades: how many trades made up the candle. taker_buy_volume: how much of the volume was
-- bought by takers, the side that did not wait. Null on candles stored before this migration;
-- the 1h/4h/1d models do not use them.
-- ---------------------------------------------------------------------------------------
alter table public.candles
  add column trades integer,
  add column taker_buy_volume numeric;

-- ---------------------------------------------------------------------------------------
-- 4. Daily summary of signals.
-- The fast sizes make about 37,600 signals a day. Their raw rows are kept for 90 days and then
-- deleted (worker job prune_fast_history); these counts stay forever, so the track record
-- never loses history. The track-record endpoints read this table for every size.
-- Everything is a plain count or sum, so days, coins and sizes can simply be added up.
-- ---------------------------------------------------------------------------------------
create table public.signal_stats_daily (
  asset_id        smallint not null references public.assets(id),
  timeframe       text not null check (timeframe in ('1m','3m','5m','15m','30m','1h','4h','1d')),
  day             date not null,              -- UTC day of the predicted candle's open time
  n_signals       integer not null,           -- signals made for candles of this day
  n_resolved      integer not null,           -- with a result: the candle closed up or down
  n_flat          integer not null,           -- the candle closed flat (fast sizes): no result
  n_went_up       integer not null,           -- of n_resolved
  n_calls         integer not null,           -- of n_resolved, signals that said Up or Down
  n_correct       integer not null,           -- of n_calls
  n_up_calls      integer not null,
  n_up_correct    integer not null,
  n_down_calls    integer not null,
  n_down_correct  integer not null,
  n_naive         integer not null,           -- of n_resolved, rows where the naive rule could answer
  n_naive_correct integer not null,           -- naive rule: "the next candle repeats the last one"
  brier_sum       double precision not null,  -- sum of (p_up - went_up)^2 over n_resolved
  updated_at      timestamptz not null default now(),
  primary key (asset_id, timeframe, day)
);

alter table public.signal_stats_daily enable row level security;
-- Public numbers, like the signals and their outcomes. Only the worker (service role) writes.
create policy "public read signal stats" on public.signal_stats_daily
  for select to anon, authenticated using (true);
