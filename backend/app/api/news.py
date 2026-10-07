"""Public news endpoint: recent headlines with the sentiment Gemini gave them."""

from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy import text

from app.api.errors import ApiError
from app.api.schemas import NewsItemOut, NewsResponse, SentimentOut
from app.api.v1 import Db
from app.data import repo
from app.data.news import SOURCE_NAMES

router = APIRouter(prefix="/v1", tags=["news"])

# A score this close to zero is shown as "Neutral" (docs/08: "Neutral +0.02").
NEUTRAL_BAND = 0.1


def sentiment_label(score: float) -> str:
    return (
        "bullish" if score >= NEUTRAL_BAND else "bearish" if score <= -NEUTRAL_BAND else "neutral"
    )


@router.get("/news", response_model=NewsResponse)
async def get_news(
    session: Db,
    symbol: Annotated[str | None, Query(max_length=10)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 30,
) -> NewsResponse:
    """Newest headlines first. With `symbol`, only headlines about that coin: tagged by
    keyword when stored, or named by Gemini when scored."""
    wanted = None
    if symbol is not None:
        asset = await repo.get_asset(session, symbol.upper())
        if asset is None:
            raise ApiError(404, "not_found", "Asset not found")
        wanted = asset.symbol
    rows = await session.execute(
        text(
            """
            select n.id, n.source, n.title, n.url, n.published_at,
                   coalesce(s.assets, n.asset_symbols) as symbols,
                   s.score, s.confidence, s.event_type, s.reason
            from news_items n
            left join sentiments s on s.news_id = n.id
            where cast(:symbol as text) is null
               or :symbol = any(n.asset_symbols)
               or :symbol = any(s.assets)
            order by n.published_at desc, n.id desc
            limit :limit
            """
        ),
        {"symbol": wanted, "limit": limit},
    )
    items = [
        NewsItemOut(
            id=row.id,
            source=row.source,
            source_name=SOURCE_NAMES.get(row.source, row.source),
            title=row.title,
            url=row.url,
            published_at=row.published_at,
            symbols=list(row.symbols),
            sentiment=None
            if row.score is None
            else SentimentOut(
                label=sentiment_label(row.score),
                score=round(row.score, 2),
                confidence=round(row.confidence, 2),
                event_type=row.event_type,
                reason=row.reason,
            ),
        )
        for row in rows
    ]
    return NewsResponse(symbol=wanted, items=items)
