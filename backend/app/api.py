from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from .db import User, get_session
from .entitlements import reserve_daily_scan, usage_today
from .security import current_user

router = APIRouter(prefix="/v1")
UserDep = Annotated[User, Depends(current_user)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


class ScanRequest(BaseModel):
    chain: str = Field(pattern=r"^[a-z0-9-]{2,20}$")
    address: str = Field(min_length=42, max_length=64)


@router.get("/me/usage")
async def usage(user: UserDep, session: SessionDep):
    plan = await reserve_daily_scan(session, user.id)
    # Reservation above is intentionally not used by the read endpoint.
    # This endpoint must not consume a scan; rollback the reservation.
    await session.rollback()
    count = await usage_today(session, user.id)
    return {"plan": plan.id, "daily_used": count, "daily_limit": plan.daily_scan_limit}


@router.post("/scan/wallet")
async def scan_wallet(payload: ScanRequest, user: UserDep, session: SessionDep):
    plan = await reserve_daily_scan(session, user.id)
    # Real scanner integration is intentionally isolated behind this contract.
    # No risk score is fabricated when blockchain intelligence is unavailable.
    return {
        "status": "ready",
        "chain": payload.chain,
        "address": payload.address.lower(),
        "plan": plan.id,
        "message": "Risk engine integration pending; no safety conclusion was generated.",
    }
