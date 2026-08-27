from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .api import router as api_router
from .config import settings
from .db import Plan, Subscription, User, get_session
from .security import create_access_token, current_user, hash_password, verify_password

app = FastAPI(title="Crypto Safety Scanner API", version="1.0.0")
if settings.cors_list:
    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_list, allow_credentials=True, allow_methods=["GET", "POST"], allow_headers=["Authorization", "Content-Type"])

Session = Annotated[AsyncSession, Depends(get_session)]
UserDep = Annotated[User, Depends(current_user)]
app.include_router(api_router)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    locale: str = Field(default="en", pattern=r"^(en|pl|de)$")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class OnboardingRequest(BaseModel):
    locale: str = Field(pattern=r"^(en|pl|de)$")
    use_case: str = Field(min_length=1, max_length=32)


@app.get("/v1/health/live")
async def liveness():
    return {"status": "ok"}


@app.post("/v1/auth/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, session: Session):
    email = payload.email.lower()
    if await session.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="Account already exists")
    user = User(email=email, password_hash=hash_password(payload.password), locale=payload.locale)
    session.add(user)
    await session.flush()
    plan = await session.scalar(select(Plan).where(Plan.id == "free", Plan.active.is_(True)))
    if not plan:
        raise HTTPException(status_code=503, detail="Plans unavailable")
    now = datetime.now(timezone.utc)
    session.add(Subscription(user_id=user.id, plan_id="free", status="active", period_start=now, period_end=now + timedelta(days=365)))
    await session.commit()
    return {"user": {"id": str(user.id), "email": user.email}, "plan": "free", "access_token": create_access_token(user.id), "token_type": "bearer"}


@app.post("/v1/auth/login")
async def login(payload: LoginRequest, session: Session):
    user = await session.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_access_token(user.id), "token_type": "bearer"}


@app.get("/v1/me")
async def me(user: UserDep):
    return {"id": str(user.id), "email": user.email, "locale": user.locale, "onboarding_completed": user.onboarding_completed}


@app.post("/v1/me/onboarding")
async def onboarding(payload: OnboardingRequest, user: UserDep, session: Session):
    user.locale = payload.locale
    user.onboarding_completed = True
    await session.commit()
    return {"status": "complete", "locale": user.locale}


@app.get("/v1/me/plan")
async def my_plan(user: UserDep, session: Session):
    row = await session.execute(select(Subscription, Plan).join(Plan, Subscription.plan_id == Plan.id).where(Subscription.user_id == user.id, Subscription.status == "active").order_by(Subscription.period_end.desc()))
    result = row.first()
    if not result:
        raise HTTPException(status_code=403, detail="No active plan")
    subscription, plan = result
    return {"plan": plan.id, "price_cents": plan.monthly_price_cents, "daily_limit": plan.daily_scan_limit, "monthly_limit": plan.monthly_scan_limit, "period_end": subscription.period_end}
