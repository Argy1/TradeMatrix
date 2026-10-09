-- Compact feature snapshot (approved by Argy 2026-10-03, docs/05 Phase 4).
--
-- Every signal stores the feature values the model saw, so it can be audited later (rule 7).
-- As JSON, that is the 33 names plus 17-digit numbers: about 1,070 bytes per signal, and the
-- main reason the database grows. The names are the same for every signal of one model, so:
--   * model_versions.feature_names  keeps the names once per model, in the model's order;
--   * predictions.feature_values    keeps only the values, as 4-byte numbers in that order
--                                   (about 160 bytes). XGBoost reads its inputs at this
--                                   precision, so these are exactly the values the model saw.
--
-- This migration only ADDS things. The old `features` JSON column stays and old rows keep it,
-- so the worker that is running during the change keeps working. Dropping `features` is a
-- later migration, after the old rows are converted and checked (python -m app.ml.snapshots).

-- ALTER TABLE needs the table to itself for a moment. If another query is in the way, a
-- waiting ALTER makes every later query on that table wait behind it, which would freeze the
-- live site and the worker. So give up after 5 seconds instead: nothing is changed, and the
-- migration can simply be run again.
set local lock_timeout = '5s';

alter table public.model_versions
  add column feature_names text[];      -- null for models stored before this migration

alter table public.predictions
  add column feature_values real[],     -- null element = "empty by design" (was JSON null)
  alter column features drop not null,
  add constraint predictions_has_snapshot
    check (features is not null or feature_values is not null);

-- One query still shows a readable snapshot, whichever way the row stores it.
-- security_invoker: the view follows the caller's own table rights and RLS. Clients cannot
-- read model_versions, so the view is for the backend and the SQL editor only.
create view public.prediction_features
with (security_invoker = true) as
select
  p.id as prediction_id,
  p.model_version_id,
  coalesce(
    p.features,
    (
      -- float8 so the JSON shows the stored value in full, whatever the session's float settings
      select jsonb_object_agg(f.name, f.value::float8)
      from unnest(m.feature_names, p.feature_values) as f(name, value)
    )
  ) as features
from public.predictions p
join public.model_versions m on m.id = p.model_version_id;

revoke all on public.prediction_features from anon, authenticated;
