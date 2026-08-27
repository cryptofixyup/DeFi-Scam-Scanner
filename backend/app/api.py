from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .db import Plan, Subscription, User, get_session
from .entitlements import reserve_daily_scan, usage_today
from .security import current_user

router = APIRouter(prefix="/v1")
UserDep = Annotated[User, Depends(current_user)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


class ScanRequest(BaseModel):
    chain: str = Field(pattern=r"^[a-z0-9-]{2,20}$")
    address: str = Field(min_length=42, max_length=64)


async def active_plan(session: AsyncSession, user_id):
    row = await session.execute(
        select(Plan)
        .join(Subscription, Subscription.plan_id == Plan.id)
        .where(Subscription.user_id == user_id, Subscription.status == "active", Plan.active.is_(True))
        .order_by(Subscription.period_end.desc())
    )
    return row.scalars().first()


@router.get("/me/usage")
async def usage(user: UserDep, session: SessionDep):
    plan = await active_plan(session, user.id)
    if not plan:
        return {"plan": None, "daily_used": 0, "daily_limit": 0}
    return {"plan": plan.id, "daily_used": await usage_today(session, user.id), "daily_limit": plan.daily_scan_limit}


@router.post("/scan/wallet")
async def scan_wallet(payload: ScanRequest, user: UserDep, session: SessionDep):
    plan = await reserve_daily_scan(session, user.id)
    return {
        "status": "ready",
        "chain": payload.chain,
        "address": payload.address.lower(),
        "plan": plan.id,
        "message": "Risk engine integration pending; no safety conclusion was generated.",
    }
