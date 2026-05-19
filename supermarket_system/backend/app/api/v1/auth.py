from datetime import timedelta

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.core.config import settings
from app.core.response import success_response
from app.core.security import create_token


router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(payload: LoginRequest, request: Request):
    # Production implementation must verify password hash and RBAC status in the database.
    access = create_token(payload.username, timedelta(minutes=settings.access_token_expire_minutes), "access")
    refresh = create_token(payload.username, timedelta(days=settings.refresh_token_expire_days), "refresh")
    return success_response({"access_token": access, "refresh_token": refresh, "token_type": "bearer"}, request.state.request_id)
