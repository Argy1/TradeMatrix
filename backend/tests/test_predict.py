"""Live prediction pieces: reasons, the prediction row, the model file and storage calls."""

import json
from datetime import UTC, datetime

import httpx
import numpy as np
import pandas as pd
import pytest

from app.features.build import build_dataset, build_features, feature_columns
from app.ml.config import NEUTRAL_HIGH, NEUTRAL_LOW, XGB_PARAMS
from app.ml.predict import label_for, make_prediction, snapshot_columns
from app.ml.reasons import build_reasons
from app.ml.registry import ModelBundle, from_bytes, to_bytes
from app.ml.storage import ModelStorage
from app.ml.train import fit_calibrated


def candles(n: int = 1500, seed: int = 11) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, n)))
    open_ = np.concatenate([[close[0]], close[:-1]])
    spread = np.abs(rng.normal(0, 0.004, n)) * close
    return pd.DataFrame(
        {
            "open": open_,
            "high": np.maximum(open_, close) + spread,
            "low": np.minimum(open_, close) - spread,
            "close": close,
            "volume": rng.uniform(10, 1000, n),
        },
        index=pd.date_range("2025-01-01", periods=n, freq="h", tz="UTC"),
    )


@pytest.fixture(scope="module")
def bundle() -> ModelBundle:
    data = build_dataset(candles())
    params = XGB_PARAMS | {"n_estimators": 30, "early_stopping_rounds": 10}
    model = fit_calibrated(
        data.iloc[:900], data.iloc[900:1100], data.iloc[1100:1400], feature_columns(data), params
    )
    return ModelBundle(model, "BTC", "1h", "test", data.index[0], data.index[899])


def test_prediction_row_is_complete_and_bounded(bundle: ModelBundle) -> None:
    result = make_prediction(bundle, candles(), None, asset_id=1)
    assert result is not None
    assert 0.01 <= result["p_up"] <= 0.99
    assert result["label"] == label_for(result["p_up"])
    # The audit snapshot: the model's features, in the model's own order.
    assert list(result["features"]) == list(bundle.model.features)
    assert 1 <= len(result["reasons"]) <= 3


def test_compact_snapshot_keeps_the_values_the_model_saw(bundle: ModelBundle) -> None:
    """Compact form = values only, in the order of the names stored on the model version."""
    data = candles()
    result = make_prediction(bundle, data, None, asset_id=1)
    features_json, values = snapshot_columns(result["features"], list(bundle.model.features))
    assert features_json is None and len(values) == len(bundle.model.features)
    # Names (stored once) + values (stored per signal) give back the same snapshot.
    assert dict(zip(bundle.model.features, values, strict=True)) == result["features"]
    # The database keeps them as 4-byte numbers, the precision XGBoost itself reads.
    seen_by_model = build_features(data).iloc[-1][bundle.model.features].to_numpy(np.float32)
    np.testing.assert_array_equal(np.array(values, dtype=np.float32), seen_by_model)


def test_snapshot_falls_back_to_json_unless_names_match_exactly(bundle: ModelBundle) -> None:
    """A list of numbers under the wrong names would be a silent error, so any doubt = JSON."""
    snapshot = make_prediction(bundle, candles(), None, asset_id=1)["features"]
    names = list(bundle.model.features)
    for stored in (None, names[::-1], names[:-1], [*names, "extra"]):
        features_json, values = snapshot_columns(snapshot, stored)
        assert values is None and json.loads(features_json) == snapshot


def test_shadow_mode_never_moves_the_probability(bundle: ModelBundle) -> None:
    shadow = make_prediction(bundle, candles(), None, 1, sentiment=0.9, blend_k=0.0)
    blended = make_prediction(bundle, candles(), None, 1, sentiment=0.9, blend_k=0.1)
    assert shadow["p_up"] == pytest.approx(min(max(shadow["p_ml"], 0.01), 0.99))
    assert blended["p_up"] > shadow["p_up"]
    # Sentiment that did not move the probability is not shown as a reason for the signal.
    assert all(reason["code"] != "sentiment" for reason in shadow["reasons"])


def test_short_history_gives_no_prediction(bundle: ModelBundle) -> None:
    assert make_prediction(bundle, candles().iloc[:30], None, 1) is None


def test_neutral_band() -> None:
    assert label_for(NEUTRAL_HIGH + 0.001) == "up"
    assert label_for(NEUTRAL_LOW - 0.001) == "down"
    assert label_for(0.5) == "neutral"


def test_reasons_are_templates_ranked_by_importance() -> None:
    features = {
        "rsi14": 78.0, "dist_ema50": 2.4, "atr_pct": 0.8, "ema_cross_3": 0.0,
        "macd_hist_pct": 0.01, "vol_ratio_20": 1.1, "bb_percent_b": 0.7, "ret_24": 0.01,
    }  # fmt: skip
    reasons = build_reasons(features, {"rsi14": 10.0, "dist_ema50": 1.0, "ret_24": 0.1})
    assert reasons[0] == {
        "code": "rsi",
        "text": "RSI 78: overbought, buyers may be stretched",
        "effect": "down",
    }
    assert len(reasons) == 3
    assert all(r["effect"] in {"up", "down", "none"} for r in reasons)


def test_model_file_round_trip(bundle: ModelBundle) -> None:
    restored = from_bytes(to_bytes(bundle))
    frame = build_dataset(candles()).iloc[-5:]
    np.testing.assert_allclose(restored.model.predict(frame), bundle.model.predict(frame))
    assert restored.timeframe == "1h" and restored.symbol == "BTC"
    # The file must name the real module, never __main__, or the worker cannot load it.
    assert b"app.ml.registry" in to_bytes(bundle) and b"__main__" not in to_bytes(bundle)


async def test_storage_uses_the_private_bucket_with_the_service_key() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, content=b"model-bytes" if request.method == "GET" else b"{}")

    http = httpx.AsyncClient(
        base_url="https://x.supabase.co/storage/v1",
        headers={"Authorization": "Bearer secret"},
        transport=httpx.MockTransport(handler),
    )
    storage = ModelStorage("https://x.supabase.co", "secret", "models", http=http)
    await storage.upload("BTC/1h/a.joblib", b"model-bytes")
    assert await storage.download("BTC/1h/a.joblib") == b"model-bytes"
    assert [r.url.path for r in seen] == ["/storage/v1/object/models/BTC/1h/a.joblib"] * 2
    assert seen[0].headers["x-upsert"] == "true"


def test_storage_refuses_to_start_without_a_key() -> None:
    with pytest.raises(ValueError):
        ModelStorage("https://x.supabase.co", "", "models")


def test_trained_at_is_utc(bundle: ModelBundle) -> None:
    assert bundle.trained_at.tzinfo is UTC and bundle.trained_at <= datetime.now(UTC)


def test_pooled_model_predicts_btc_without_btc_context() -> None:
    """Pooled 1d model: BTC rows have no BTC-context columns, in training and live."""
    btc_data = build_dataset(candles(seed=1))
    eth_data = build_dataset(candles(seed=2), candles(seed=1))
    pooled = pd.concat([btc_data.assign(asset_id=1.0), eth_data.assign(asset_id=2.0)]).sort_index(
        kind="stable"
    )
    params = XGB_PARAMS | {"n_estimators": 20, "early_stopping_rounds": 5}
    times = pooled.index
    cut1, cut2 = times[1800], times[2200]
    model = fit_calibrated(
        pooled[times < cut1],
        pooled[(times >= cut1) & (times < cut2)],
        pooled[times >= cut2],
        feature_columns(pooled),
        params,
    )
    bundle = ModelBundle(model, "ALL", "1d", "test", times[0], cut1)
    result = make_prediction(bundle, candles(seed=1), None, asset_id=1)
    assert result is not None
    assert result["features"]["btc_ret_1"] is None  # empty by design, stored as null
    assert result["features"]["asset_id"] == 1.0
    # Compact form: the empty value keeps its place in the list, so the order never shifts.
    _, values = snapshot_columns(result["features"], list(bundle.model.features))
    assert values[bundle.model.features.index("btc_ret_1")] is None
    assert values[bundle.model.features.index("asset_id")] == 1.0
