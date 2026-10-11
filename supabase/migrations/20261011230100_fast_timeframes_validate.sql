-- Second half of 20261011230000_fast_timeframes.sql: check the rows that existed before.
--
-- "validate constraint" reads the whole table, but with a light lock: reads and writes go on
-- while it runs. It is a separate migration because a migration is one transaction, and the
-- heavy lock taken by "add constraint" in the first file is only released when that
-- transaction ends.
set local lock_timeout = '5s';

alter table public.candles validate constraint candles_timeframe_check;
alter table public.model_versions validate constraint model_versions_timeframe_check;
alter table public.predictions validate constraint predictions_timeframe_check;
alter table public.alerts validate constraint alerts_timeframe_check;
alter table public.prediction_outcomes
  validate constraint prediction_outcomes_actual_direction_check;
