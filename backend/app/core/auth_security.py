from typing import Optional, Dict, Any, TypedDict
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
import httpx
from .settings import settings

class UserInfo(TypedDict, total=False):
    id: str
    email: Optional[str]
    claims: Dict[str, Any]

bearer = HTTPBearer(auto_error=False)  # In LOCAL_DEV without SUPABASE_URL, missing creds yields stub user
_jwks_cache: Optional[Dict[str, Any]] = None

STUB_USER: UserInfo = {"id": "local-user", "email": "local@example.com", "claims": {"mode": "LOCAL_DEV"}}

async def _get_jwks() -> Dict[str, Any]:
    global _jwks_cache
    if _jwks_cache:
        return _jwks_cache
    # Local dev with no configured SUPABASE_URL: skip remote fetch entirely
    if settings.LOCAL_DEV and not settings.SUPABASE_URL:
        _jwks_cache = {"keys": []}
        return _jwks_cache
    base = settings.SUPABASE_URL.rstrip("/") if settings.SUPABASE_URL else ""
    if not base and not settings.SUPABASE_JWKS_URL:
        # Misconfiguration: no way to resolve JWKS
        _jwks_cache = {"keys": []}
        return _jwks_cache
    url = settings.SUPABASE_JWKS_URL or (base + "/auth/v1/keys")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url)
            r.raise_for_status()
            data = r.json()
            # Basic shape validation
            if not isinstance(data, dict) or "keys" not in data:
                raise ValueError("JWKS payload missing 'keys'")
            _jwks_cache = data
            return _jwks_cache
    except Exception:
        # Cache an empty structure to avoid hammering in failure loops
        _jwks_cache = {"keys": []}
        return _jwks_cache

async def current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> UserInfo:
    if not creds:
        if settings.LOCAL_DEV:
            return STUB_USER
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = creds.credentials
    jwks = await _get_jwks()
    if not jwks.get("keys"):
        if settings.LOCAL_DEV:
            # Treat any presented token as stub user in purely local mode
            return STUB_USER
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="JWKS not available")
    unverified = jwt.get_unverified_header(token)
    kid = unverified.get("kid")
    key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
    if not key:
        raise HTTPException(status_code=401, detail="Signing key not found")
    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=[key.get("alg", "RS256")],
            audience=settings.API_AUDIENCE or None,
            options={"verify_aud": bool(settings.API_AUDIENCE)}
        )
        iss = payload.get("iss")
        if settings.API_ISSUER and iss != settings.API_ISSUER:
            raise HTTPException(status_code=401, detail="Invalid issuer")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
    user_id = payload.get("sub") or payload.get("user_id")
    email = payload.get("email") or payload.get("user_metadata", {}).get("email")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing subject")
    return {"id": user_id, "email": email, "claims": payload}

def require_auth(user = Depends(current_user)):
    return user