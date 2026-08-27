from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .db import ScamWallet, Scan, User, get_session
from .entitlements import active_plan, reserve_daily_scan, usage_month, usage_today
from .evm import EVMRPC, InvalidEVMAddress, normalize_evm_address
from .risk import score_observation
from .security import current_user

router = APIRouter(prefix="/v1")
UserDep = Annotated[User, Depends(current_user)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


class ScanRequest(BaseModel):
    model_config = {"extra": "forbid"}
    chain: str = Field(pattern=r"^[a-z0-9-]{2,20}$")
    address: str = Field(min_length=42, max_length=42)


@router.get("/me/usage")
async def usage(user: UserDep, session: SessionDep):
    plan = await active_plan(session, user.id)
    return {
        "plan": plan.id,
        "daily_used": await usage_today(session, user.id),
        "daily_limit": plan.daily_scan_limit,
        "monthly_used": await usage_month(session, user.id),
        "monthly_limit": plan.monthly_scan_limit,
    }


@router.post("/scan/wallet")
async def scan_wallet(payload: ScanRequest, user: UserDep, session: SessionDep):
    try:
        address = normalize_evm_address(payload.address)
    except InvalidEVMAddress:
        raise HTTPException(status_code=422, detail="Invalid EVM address") from None
    if payload.chain != "ethereum":
        raise HTTPException(status_code=422, detail="Unsupported chain")
    if not settings.ethereum_rpc_url:
        raise HTTPException(status_code=503, detail="Blockchain provider unavailable")

    plan = await reserve_daily_scan(session, user.id)
    scam = await session.scalar(select(ScamWallet).where(ScamWallet.chain == payload.chain, ScamWallet.address == address))
    try:
        observation = await EVMRPC(settings.ethereum_rpc_url).observe(payload.chain, address)
    except Exception:
        raise HTTPException(status_code=503, detail="Blockchain data temporarily unavailable") from None

    result = score_observation(observation, None if scam is None else {"severity": scam.severity, "category": scam.category, "source": scam.source})
    scan = Scan(user_id=user.id, chain=payload.chain, address=address, score=result["score"], risk=result["risk"], confidence=result["confidence"], status=result["status"], engine_version=result["engine_version"], evidence=result["evidence"])
    session.add(scan)
    await session.commit()
    return {"scan_id": str(scan.id), "chain": payload.chain, "address": address, "plan": plan.id, **result}
