"""Alert rules and in-app notifications of the signed-in user.

Like every protected endpoint (docs/04): the database role of the API bypasses RLS, so EVERY
query here filters by the user id from the verified token. A rule or notification that
belongs to someone else is answered with 404, the same as one that does not exist.
"""

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any, Literal, Self
from uuid import UUID

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.alerts.rules import PRICE_TYPES, SIGNAL_TYPES
from app.api.auth import CurrentUser
from app.api.errors import ApiError
from app.api.v1 import Db
from app.data import repo
from app.timeframes import Timeframe

router = APIRouter(prefix="/v1", tags=["alerts"])

MAX_ALERTS = 20  # per user; keeps the worker's checks small and stops abuse
MAX_COOLDOWN = 7 * 24 * 60  # one week, in minutes

AlertType = Literal["signal_change", "prob_above", "prob_below", "price_above", "price_below"]


def check_threshold(alert_type: str, threshold: Decimal | None) -> None:
    """The threshold means a probability, a price or nothing, depending on the type."""
    if alert_type == "signal_change":
        if threshold is not None:
            raise ValueError("signal_change alerts have no threshold")
    elif threshold is None:
        raise ValueError("threshold is required for this alert type")
    elif alert_type in SIGNAL_TYPES:
        if not 0 < threshold < 1:
            raise ValueError("threshold must be a probability between 0 and 1")
    elif threshold <= 0:
        raise ValueError("threshold must be a price above 0")


class AlertIn(BaseModel):
    symbol: str = Field(min_length=1, max_length=10)
    type: AlertType
    timeframe: Timeframe | None = None  # needed for signal alerts, not allowed for price alerts
    threshold: Decimal | None = Field(default=None, max_digits=20, decimal_places=8)
    cooldown_minutes: int = Field(default=60, ge=1, le=MAX_COOLDOWN)

    @model_validator(mode="after")
    def fields_fit_the_type(self) -> Self:
        if self.type in SIGNAL_TYPES and self.timeframe is None:
            raise ValueError("timeframe is required for signal alerts")
        if self.type in PRICE_TYPES and self.timeframe is not None:
            raise ValueError("price alerts have no timeframe")
        check_threshold(self.type, self.threshold)
        return self


class AlertPatch(BaseModel):
    """Only the fields that are sent are changed."""

    active: bool | None = None
    threshold: Decimal | None = Field(default=None, max_digits=20, decimal_places=8)
    cooldown_minutes: int | None = Field(default=None, ge=1, le=MAX_COOLDOWN)


class AlertOut(BaseModel):
    id: UUID
    symbol: str
    type: str
    timeframe: str | None
    threshold: str | None  # a string, like prices: no float rounding on the way
    cooldown_minutes: int
    active: bool
    last_triggered_at: datetime | None
    created_at: datetime


class AlertsOut(BaseModel):
    items: list[AlertOut]
    max_alerts: int = MAX_ALERTS


class NotificationOut(BaseModel):
    id: int
    title: str
    body: str
    data: dict[str, Any]
    created_at: datetime
    read_at: datetime | None


class NotificationsOut(BaseModel):
    items: list[NotificationOut]
    unread: int


_ALERT_COLUMNS = """
    al.id, a.symbol, al.type, al.timeframe, al.threshold, al.cooldown_minutes, al.active,
    al.last_triggered_at, al.created_at
"""


def _alert(row: Any) -> AlertOut:
    return AlertOut(
        id=row.id,
        symbol=row.symbol,
        type=row.type,
        timeframe=row.timeframe,
        threshold=None if row.threshold is None else format(row.threshold.normalize(), "f"),
        cooldown_minutes=row.cooldown_minutes,
        active=row.active,
        last_triggered_at=row.last_triggered_at,
        created_at=row.created_at,
    )


async def list_alerts(session: AsyncSession, user_id: UUID) -> list[AlertOut]:
    rows = await session.execute(
        text(
            f"select {_ALERT_COLUMNS} from alerts al join assets a on a.id = al.asset_id "
            "where al.user_id = :uid order by al.created_at desc"
        ),
        {"uid": user_id},
    )
    return [_alert(row) for row in rows]


async def get_alert(session: AsyncSession, user_id: UUID, alert_id: UUID) -> AlertOut | None:
    row = (
        await session.execute(
            text(
                f"select {_ALERT_COLUMNS} from alerts al join assets a on a.id = al.asset_id "
                "where al.user_id = :uid and al.id = :id"
            ),
            {"uid": user_id, "id": alert_id},
        )
    ).first()
    return _alert(row) if row else None


async def create_alert(
    session: AsyncSession, user_id: UUID, asset_id: int, body: AlertIn
) -> UUID | None:
    """Insert the rule unless the user already has MAX_ALERTS; returns the new id or None.

    The count and the insert are one statement, so two requests at the same moment cannot
    both slip under the limit.
    """
    new_id = (
        await session.execute(
            text(
                """
                insert into alerts (user_id, asset_id, timeframe, type, threshold, cooldown_minutes)
                select cast(:uid as uuid), cast(:asset_id as smallint), cast(:timeframe as text),
                       cast(:type as text), cast(:threshold as numeric), cast(:cooldown as integer)
                where (select count(*) from alerts where user_id = cast(:uid as uuid))
                      < cast(:max_alerts as integer)
                returning id
                """
            ),
            {
                "uid": user_id,
                "asset_id": asset_id,
                "timeframe": body.timeframe,
                "type": body.type,
                "threshold": body.threshold,
                "cooldown": body.cooldown_minutes,
                "max_alerts": MAX_ALERTS,
            },
        )
    ).scalar_one_or_none()
    await session.commit()
    return new_id


async def update_alert(
    session: AsyncSession, user_id: UUID, alert_id: UUID, changes: dict[str, Any]
) -> None:
    await session.execute(
        text(
            """
            update alerts set
              active = coalesce(cast(:active as boolean), active),
              threshold = coalesce(cast(:threshold as numeric), threshold),
              cooldown_minutes = coalesce(cast(:cooldown_minutes as integer), cooldown_minutes)
            where user_id = :uid and id = :id
            """
        ),
        {
            "uid": user_id,
            "id": alert_id,
            "active": changes.get("active"),
            "threshold": changes.get("threshold"),
            "cooldown_minutes": changes.get("cooldown_minutes"),
        },
    )
    await session.commit()


async def delete_alert(session: AsyncSession, user_id: UUID, alert_id: UUID) -> bool:
    deleted = await session.execute(
        text("delete from alerts where user_id = :uid and id = :id returning id"),
        {"uid": user_id, "id": alert_id},
    )
    found = deleted.first() is not None
    await session.commit()
    return found


async def list_notifications(session: AsyncSession, user_id: UUID, limit: int) -> NotificationsOut:
    rows = await session.execute(
        text(
            "select id, title, body, data, created_at, read_at from notifications "
            "where user_id = :uid order by created_at desc, id desc limit :limit"
        ),
        {"uid": user_id, "limit": limit},
    )
    unread = await session.execute(
        text("select count(*) from notifications where user_id = :uid and read_at is null"),
        {"uid": user_id},
    )
    return NotificationsOut(
        items=[NotificationOut(**row._mapping) for row in rows], unread=unread.scalar_one()
    )


async def mark_read(
    session: AsyncSession, user_id: UUID, notification_id: int
) -> NotificationOut | None:
    row = (
        await session.execute(
            text(
                # coalesce: marking twice keeps the first time (idempotent)
                "update notifications set read_at = coalesce(read_at, now()) "
                "where user_id = :uid and id = :id "
                "returning id, title, body, data, created_at, read_at"
            ),
            {"uid": user_id, "id": notification_id},
        )
    ).first()
    await session.commit()
    return NotificationOut(**row._mapping) if row else None


def _not_found() -> ApiError:
    return ApiError(404, "not_found", "Alert not found")


@router.get("/alerts", response_model=AlertsOut)
async def get_alerts(session: Db, user: CurrentUser) -> AlertsOut:
    return AlertsOut(items=await list_alerts(session, user.user_id))


@router.post("/alerts", response_model=AlertOut, status_code=201)
async def post_alert(session: Db, user: CurrentUser, body: AlertIn) -> AlertOut:
    asset = await repo.get_asset(session, body.symbol.upper())
    if asset is None:
        raise ApiError(404, "not_found", "Asset not found")
    alert_id = await create_alert(session, user.user_id, asset.id, body)
    if alert_id is None:
        raise ApiError(409, "alert_limit", f"You can have at most {MAX_ALERTS} alerts")
    created = await get_alert(session, user.user_id, alert_id)
    if created is None:  # deleted by another request in the same instant
        raise _not_found()
    return created


@router.patch("/alerts/{alert_id}", response_model=AlertOut)
async def patch_alert(session: Db, user: CurrentUser, alert_id: UUID, body: AlertPatch) -> AlertOut:
    current = await get_alert(session, user.user_id, alert_id)
    if current is None:
        raise _not_found()
    changes = body.model_dump(exclude_unset=True, exclude_none=True)
    if "threshold" in changes:
        try:
            check_threshold(current.type, changes["threshold"])
        except ValueError as exc:
            raise ApiError(422, "validation_error", f"threshold: {exc}") from exc
    if changes:
        await update_alert(session, user.user_id, alert_id, changes)
    updated = await get_alert(session, user.user_id, alert_id)
    if updated is None:
        raise _not_found()
    return updated


@router.delete("/alerts/{alert_id}", response_model=AlertsOut)
async def remove_alert(session: Db, user: CurrentUser, alert_id: UUID) -> AlertsOut:
    if not await delete_alert(session, user.user_id, alert_id):
        raise _not_found()
    return AlertsOut(items=await list_alerts(session, user.user_id))


@router.get("/notifications", response_model=NotificationsOut)
async def get_notifications(
    session: Db, user: CurrentUser, limit: Annotated[int, Query(ge=1, le=100)] = 50
) -> NotificationsOut:
    return await list_notifications(session, user.user_id, limit)


@router.post("/notifications/{notification_id}/read", response_model=NotificationOut)
async def read_notification(
    session: Db, user: CurrentUser, notification_id: int
) -> NotificationOut:
    notification = await mark_read(session, user.user_id, notification_id)
    if notification is None:
        raise ApiError(404, "not_found", "Notification not found")
    return notification
