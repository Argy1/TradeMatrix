"""Endpoints for a signed-in user (Authorization: Bearer <Supabase access token>).

The API connects with a privileged database role that bypasses RLS, so EVERY query here filters
by the user id from the verified token (docs/04 security model).
"""

from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import CurrentUser
from app.api.errors import ApiError
from app.api.v1 import Db
from app.data import repo

router = APIRouter(prefix="/v1", tags=["account"])


class WatchlistOut(BaseModel):
    symbols: list[str]


async def watchlist_symbols(session: AsyncSession, user_id: UUID) -> list[str]:
    rows = await session.execute(
        text(
            "select a.symbol from watchlists w join assets a on a.id = w.asset_id "
            "where w.user_id = :uid order by w.created_at"
        ),
        {"uid": user_id},
    )
    return [row[0] for row in rows]


async def add_to_watchlist(session: AsyncSession, user_id: UUID, asset_id: int) -> None:
    await session.execute(
        text(
            "insert into watchlists (user_id, asset_id) values (:uid, :aid) "
            "on conflict (user_id, asset_id) do nothing"  # adding twice is fine (idempotent)
        ),
        {"uid": user_id, "aid": asset_id},
    )
    await session.commit()


async def remove_from_watchlist(session: AsyncSession, user_id: UUID, asset_id: int) -> None:
    await session.execute(
        text("delete from watchlists where user_id = :uid and asset_id = :aid"),
        {"uid": user_id, "aid": asset_id},
    )
    await session.commit()


async def _asset_id(session: AsyncSession, symbol: str) -> int:
    asset = await repo.get_asset(session, symbol.upper())
    if asset is None:
        raise ApiError(404, "not_found", "Asset not found")
    return asset.id


@router.get("/watchlist", response_model=WatchlistOut)
async def get_watchlist(session: Db, user: CurrentUser) -> WatchlistOut:
    return WatchlistOut(symbols=await watchlist_symbols(session, user.user_id))


@router.put("/watchlist/{symbol}", response_model=WatchlistOut)
async def put_watchlist(session: Db, user: CurrentUser, symbol: str) -> WatchlistOut:
    await add_to_watchlist(session, user.user_id, await _asset_id(session, symbol))
    return WatchlistOut(symbols=await watchlist_symbols(session, user.user_id))


@router.delete("/watchlist/{symbol}", response_model=WatchlistOut)
async def delete_watchlist(session: Db, user: CurrentUser, symbol: str) -> WatchlistOut:
    await remove_from_watchlist(session, user.user_id, await _asset_id(session, symbol))
    return WatchlistOut(symbols=await watchlist_symbols(session, user.user_id))
