from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from .db import User, get_session
from .entitlements import active_plan, reserve_daily_scan, usage_month, usage_today
from .security import current_user

router = APIRouter(prefix="/v1")
UserDep = Annotated[User, Depends(current_user)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


class ScanRequest(BaseModel):
    model_config = {"extra": "forbid"}
    chain: str = Field(pattern=r"^[a-z0-9-]{2,20}$")
    address: str = Field(min_length=42, max_length=64)


@router.get("/me/usage")
async def usage(user: UserDep, session: SessionDep):
    plan = await active_plan(session, user.id)
    if plan is None:
        return {"plan": None, "daily_used": 0, "daily_limit": 0, "monthly_used": 0, "monthly_limit": 0}
    return {
        "plan": plan.id,
        "daily_used": await usage_today(session, user.id),
        "daily_limit": plan.daily_scan_limit,
        "monthly_used": await usage_month(session, user.id),
        "monthly_limit": plan.monthly_scan_limit,
    }


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
