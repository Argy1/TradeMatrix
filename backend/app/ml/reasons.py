"""The "Why this signal" lines: fixed templates filled from the feature snapshot (docs/03).

Never free text from an LLM. Each candidate reason gets a score = how much the model relied on
that feature (importance) x how unusual its value is right now; the top 3 are shown.
`effect` is the classic chart reading of the indicator (docs/08 tags "Pushes up" / "Pushes
down" / "No clear push"), not a claim about the model's internal reasoning.
"""

from collections.abc import Mapping


def _candidates(
    f: Mapping[str, float], sentiment: float | None
) -> list[tuple[str, str, str, float, str]]:
    """(code, text, effect, how unusual 0..~3, feature name)."""
    out = []
    rsi = f["rsi14"]
    if rsi >= 70:
        out.append(
            (
                "rsi",
                f"RSI {rsi:.0f}: overbought, buyers may be stretched",
                "down",
                1 + (rsi - 70) / 10,
                "rsi14",
            )
        )
    elif rsi <= 30:
        out.append(
            (
                "rsi",
                f"RSI {rsi:.0f}: oversold, sellers may be stretched",
                "up",
                1 + (30 - rsi) / 10,
                "rsi14",
            )
        )
    else:
        effect = "up" if rsi > 55 else "down" if rsi < 45 else "none"
        out.append(
            (
                "rsi",
                f"RSI {rsi:.0f}: momentum {'up' if rsi > 55 else 'down' if rsi < 45 else 'flat'}",
                effect,
                abs(rsi - 50) / 20,
                "rsi14",
            )
        )

    dist = f["dist_ema50"]
    side = "above" if dist >= 0 else "below"
    out.append(
        (
            "ema_trend",
            f"Close {side} EMA 50 by {abs(dist):.1f}%",
            "up" if dist >= 0 else "down",
            abs(dist) / max(f.get("atr_pct", 1.0), 0.1),
            "dist_ema50",
        )
    )

    cross = f.get("ema_cross_3", 0.0)
    if cross > 0:
        out.append(
            (
                "ema_cross",
                "EMA 9 crossed above EMA 21 in the last 3 candles",
                "up",
                1.5,
                "ema_cross_3",
            )
        )
    elif cross < 0:
        out.append(
            (
                "ema_cross",
                "EMA 9 crossed below EMA 21 in the last 3 candles",
                "down",
                1.5,
                "ema_cross_3",
            )
        )

    hist = f["macd_hist_pct"]
    out.append(
        (
            "macd",
            f"MACD histogram {'positive' if hist >= 0 else 'negative'}",
            "up" if hist >= 0 else "down",
            min(abs(hist) * 20, 3.0),
            "macd_hist_pct",
        )
    )

    volume = f["vol_ratio_20"]
    if volume >= 1.5:
        out.append(
            (
                "volume",
                f"Volume {volume:.1f}x its 20-candle average",
                "none",
                volume - 1,
                "vol_ratio_20",
            )
        )

    percent_b = f["bb_percent_b"]
    if percent_b > 1:
        out.append(
            (
                "bollinger",
                "Price above the upper Bollinger Band",
                "down",
                1 + (percent_b - 1) * 2,
                "bb_percent_b",
            )
        )
    elif percent_b < 0:
        out.append(
            (
                "bollinger",
                "Price below the lower Bollinger Band",
                "up",
                1 - percent_b * 2,
                "bb_percent_b",
            )
        )

    move = f["ret_24"] * 100
    out.append(
        (
            "momentum",
            f"{'Up' if move >= 0 else 'Down'} {abs(move):.1f}% over the last 24 candles",
            "up" if move >= 0 else "down",
            abs(move) / max(f.get("atr_pct", 1.0) * 5, 0.1),
            "ret_24",
        )
    )

    if sentiment:
        out.append(
            (
                "sentiment",
                f"News sentiment {sentiment:+.2f}",
                "up" if sentiment > 0 else "down",
                abs(sentiment) * 3,
                "",
            )
        )
    return out  # fmt: skip


def build_reasons(
    features: Mapping[str, float],
    importances: Mapping[str, float],
    sentiment: float | None = None,
    limit: int = 3,
) -> list[dict[str, str]]:
    top = max(importances.values(), default=0.0) or 1.0
    scored = []
    for code, text, effect, unusual, feature in _candidates(features, sentiment):
        # Features the model barely used still count a little, so a strong reading can show.
        weight = 0.25 + importances.get(feature, top * 0.5 if not feature else 0.0) / top
        scored.append((weight * unusual, {"code": code, "text": text, "effect": effect}))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [reason for _, reason in scored[:limit]]
