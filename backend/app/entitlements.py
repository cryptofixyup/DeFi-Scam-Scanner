from datetime import date, datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from .db import Plan, Subscription, UsageCounter


async def active_plan(session: AsyncSession, user_id: UUID) -> Plan:
    now = datetime.now(timezone.utc)
    row = await session.execute(
        select(Plan)
        .join(Subscription, Subscription.plan_id == Plan.id)
        .where(
            Subscription.user_id == user_id,
            Subscription.status == "active",
            Subscription.period_start <= now,
            Subscription.period_end > now,
            Plan.active.is_(True),
        )
        .order_by(Subscription.period_end.desc())
    )
    plan = row.scalars().first()
    if plan is None:
        raise HTTPException(status_code=403, detail="No active plan")
    return plan


async def reserve_daily_scan(session: AsyncSession, user_id: UUID) -> Plan:
    plan = await active_plan(session, user_id)
    today = date.today()
    month_total = await usage_month(session, user_id)
    if month_total >= plan.monthly_scan_limit:
        raise HTTPException(status_code=429, detail="Monthly scan limit reached")

    stmt = insert(UsageCounter).values(user_id=user_id, usage_date=today, scan_count=1)
    stmt = stmt.on_conflict_do_update(
        index_elements=[UsageCounter.user_id, UsageCounter.usage_date],
        set_={"scan_count": UsageCounter.scan_count + 1},
        where=UsageCounter.scan_count < plan.daily_scan_limit,
    ).returning(UsageCounter.scan_count)
    result = await session.execute(stmt)
    count = result.scalar_one_or_none()
    if count is None:
        await session.rollback()
        raise HTTPException(status_code=429, detail="Daily scan limit reached")
    await session.commit()
    return plan


async def release_scan(session: AsyncSession, user_id: UUID) -> None:
    today = date.today()
    await session.execute(
        UsageCounter.__table__.update()
        .where(UsageCounter.user_id == user_id, UsageCounter.usage_date == today, UsageCounter.scan_count > 0)
        .values(scan_count=UsageCounter.scan_count - 1)
    )
    await session.commit()


async def usage_today(session: AsyncSession, user_id: UUID) -> int:
    value = await session.scalar(select(UsageCounter.scan_count).where(UsageCounter.user_id == user_id, UsageCounter.usage_date == date.today()))
    return int(value or 0)


async def usage_month(session: AsyncSession, user_id: UUID) -> int:
    first_day = date.today().replace(day=1)
    value = await session.scalar(
        select(func.coalesce(func.sum(UsageCounter.scan_count), 0)).where(
            UsageCounter.user_id == user_id,
            UsageCounter.usage_date >= first_day,
        )
    )
    return int(value or 0)
