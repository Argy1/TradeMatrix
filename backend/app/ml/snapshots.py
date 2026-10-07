"""Move the audit snapshots of old signals to the compact form (docs/05, Phase 4).

    uv run python -m app.ml.snapshots               # names + convert + check, then a report
    uv run python -m app.ml.snapshots --clear-json  # later: also remove the JSON that was converted

New signals are written compact by the worker (app.ml.predict.snapshot_columns). This command
is for what existed before: models without stored feature names and signals that only have
the `features` JSON. Every step can be run again without doing anything twice.

1. names:   copy each model's feature list from its file into model_versions.feature_names.
2. convert: copy an old signal's JSON values into feature_values, in the model's order.
3. check:   read the values back by position and compare them with the JSON by name.
            Any difference rolls the whole run back, so nothing is half converted.
4. clear:   only with --clear-json: set `features` to null where the compact copy exists.
"""

import argparse
import asyncio
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app import db
from app.config import get_settings
from app.ml.registry import from_bytes
from app.ml.storage import ModelStorage

# `:model_id` limits a step to one model version (the tests use it); null means every row.
_ONLY = "(cast(:model_id as integer) is null or p.model_version_id = :model_id)"

# Only rows whose JSON has exactly the model's feature names: then "value by name" and
# "value by position" are the same thing and nothing can be lost or misplaced.
CONVERT = f"""
update predictions p
set feature_values = (
  select array_agg((p.features ->> f.name)::real order by f.ord)
  from model_versions m, unnest(m.feature_names) with ordinality as f(name, ord)
  where m.id = p.model_version_id
)
where p.feature_values is null
  and p.features is not null
  and {_ONLY}
  and exists (
    select 1 from model_versions m
    where m.id = p.model_version_id
      and (select array_agg(k order by k) from jsonb_object_keys(p.features) as k)
        = (select array_agg(n order by n) from unnest(m.feature_names) as n)
  )
"""

# A signal that has both forms must tell the same story in both. unnest() pads the shorter
# list with nulls, so a missing name or a missing value also counts as a mismatch.
MISMATCHES = f"""
select count(distinct p.id)
from predictions p
join model_versions m on m.id = p.model_version_id
cross join lateral unnest(m.feature_names, p.feature_values) as f(name, value)
where p.features is not null
  and p.feature_values is not null
  and {_ONLY}
  and (f.name is null
       or not jsonb_exists(p.features, f.name)
       or (p.features ->> f.name)::real is distinct from f.value)
"""

CLEAR = f"""
update predictions p set features = null
where p.features is not null and p.feature_values is not null and {_ONLY}
"""

REPORT = """
select
  count(*) as signals,
  count(*) filter (where feature_values is not null and features is null) as compact,
  count(*) filter (where feature_values is not null and features is not null) as both,
  count(*) filter (where feature_values is null) as json_only,
  (select count(*) from model_versions where feature_names is null) as models_without_names
from predictions
"""


async def models_without_names(session: AsyncSession) -> list[tuple[int, str]]:
    rows = await session.execute(
        text("select id, artifact_path from model_versions where feature_names is null order by id")
    )
    return [(row.id, row.artifact_path) for row in rows]


async def set_feature_names(session: AsyncSession, model_id: int, names: list[str]) -> None:
    await session.execute(
        text(
            "update model_versions set feature_names = cast(:names as text[]) "
            "where id = :id and feature_names is null"
        ),
        {"id": model_id, "names": list(names)},
    )


async def convert_json_rows(session: AsyncSession, model_id: int | None = None) -> int:
    return (await session.execute(text(CONVERT), {"model_id": model_id})).rowcount


async def count_mismatches(session: AsyncSession, model_id: int | None = None) -> int:
    return (await session.execute(text(MISMATCHES), {"model_id": model_id})).scalar_one()


async def clear_json_rows(session: AsyncSession, model_id: int | None = None) -> int:
    return (await session.execute(text(CLEAR), {"model_id": model_id})).rowcount


async def run(clear_json: bool) -> int:
    settings = get_settings()
    factory = db.session_factory()
    if factory is None:
        print("DATABASE_URL is not configured")
        return 1
    storage = ModelStorage(
        settings.supabase_url, settings.supabase_service_role_key, settings.supabase_models_bucket
    )
    try:
        async with factory() as session:
            todo = await models_without_names(session)
        # Download before opening the write transaction, so it stays short.
        names: dict[str, list[str]] = {}
        failed: list[str] = []
        for _, path in todo:
            if path in names or path in failed:
                continue  # the pooled 1d file is shared by every coin
            try:
                names[path] = list(from_bytes(await storage.download(path)).model.features)
            except Exception as exc:  # a missing file leaves that model's signals as JSON
                failed.append(path)
                print(f"could not read {path}: {type(exc).__name__}: {exc}")

        async with factory() as session, session.begin():
            for model_id, path in todo:
                if path in names:
                    await set_feature_names(session, model_id, names[path])
            converted = await convert_json_rows(session)
            mismatches = await count_mismatches(session)
            if mismatches:
                # Raising inside `session.begin()` rolls back the names and the conversion too.
                raise RuntimeError(f"{mismatches} signals differ between JSON and compact form")
            cleared = await clear_json_rows(session) if clear_json else 0
            report = (await session.execute(text(REPORT))).one()
    except RuntimeError as exc:
        print(f"nothing was changed: {exc}")
        return 1
    finally:
        await storage.aclose()
        engine = db.get_engine()
        if engine is not None:
            await engine.dispose()

    print(
        f"models named: {len(todo) - sum(path in failed for _, path in todo)} of {len(todo)}, "
        f"signals converted: {converted}, JSON cleared: {cleared}"
    )
    print(
        f"signals: {report.signals} total, {report.compact} compact, {report.both} with both "
        f"forms, {report.json_only} JSON only; models without names: {report.models_without_names}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert old audit snapshots to compact form.")
    parser.add_argument(
        "--clear-json",
        action="store_true",
        help="also remove the JSON of signals that have a checked compact copy",
    )
    return asyncio.run(run(parser.parse_args().clear_json))


if __name__ == "__main__":
    sys.exit(main())
