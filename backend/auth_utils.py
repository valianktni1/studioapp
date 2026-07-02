import os
import jwt
import bcrypt
from datetime import datetime, timezone, timedelta
from fastapi import Request, HTTPException, Depends

from db import db

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_DAYS = 7


def get_jwt_secret() -> str:
    return os.environ["JWT_SECRET"]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def create_token(payload: dict) -> str:
    data = dict(payload)
    data["exp"] = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_DAYS)
    return jwt.encode(data, get_jwt_secret(), algorithm=JWT_ALGORITHM)


def _decode(request: Request) -> dict:
    auth = request.headers.get("Authorization", "")
    token = auth[7:] if auth.startswith("Bearer ") else request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_super_admin(request: Request) -> dict:
    payload = _decode(request)
    if payload.get("role") != "super_admin":
        raise HTTPException(status_code=403, detail="Super admin access required")
    sa = await db.super_admins.find_one({"id": payload.get("sub")})
    if not sa:
        raise HTTPException(status_code=401, detail="Account not found")
    return {"id": sa["id"], "username": sa["username"], "role": "super_admin"}


async def get_current_tenant(request: Request) -> dict:
    """Returns tenant context for tenant admins (or super admin impersonating)."""
    payload = _decode(request)
    role = payload.get("role")
    if role not in ("tenant_admin",):
        raise HTTPException(status_code=403, detail="Tenant access required")
    tenant_id = payload.get("tenant_id")
    admin = await db.admins.find_one({"id": payload.get("sub"), "tenant_id": tenant_id})
    if not admin:
        raise HTTPException(status_code=401, detail="Account not found")
    tenant = await db.tenants.find_one({"id": tenant_id})
    if not tenant:
        raise HTTPException(status_code=401, detail="Tenant not found")
    if tenant.get("suspended"):
        raise HTTPException(status_code=403, detail="Account suspended, contact support")
    return {
        "admin_id": admin["id"],
        "tenant_id": tenant_id,
        "email": admin.get("email"),
        "tenant": _clean(tenant),
        "impersonated_by": payload.get("impersonated_by"),
    }


def _clean(doc: dict) -> dict:
    if not doc:
        return doc
    doc = dict(doc)
    doc.pop("_id", None)
    doc.pop("password_hash", None)
    doc.pop("totp_secret", None)
    return doc
