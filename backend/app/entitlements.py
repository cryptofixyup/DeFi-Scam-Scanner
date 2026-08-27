from datetime import date
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from .db import Plan, Subscription, UsageCounter


async def reserve_daily_scan(session: AsyncSession, user_id: UUID) -> Plan:
    row = await session.execute(
        select(Subscription, Plan)
        .join(Plan, Subscription.plan_id == Plan.id)
        .where(Subscription.user_id == user_id, Subscription.status == "active", Plan.active.is_(True))
        .order_by(Subscription.period_end.desc())
    )
    result = row.first()
    if not result:
        raise HTTPException(status_code=403, detail="No active plan")
    subscription, plan = result

    today = date.today()
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


async def usage_today(session: AsyncSession, user_id: UUID) -> int:
    row = await session.scalar(select(UsageCounter.scan_count).where(UsageCounter.user_id == user_id, UsageCounter.usage_date == date.today()))
    return row or 0
