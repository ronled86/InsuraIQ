"""
API Key management routes (admin only)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Optional
from pydantic import BaseModel
from ..core.api_key_manager import api_key_manager
from ..core.auth_security import require_auth
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/keys", tags=["admin", "api-keys"])

class KeyGenerateRequest(BaseModel):
    service_name: str
    expires_days: int = 90

class KeyRotateRequest(BaseModel):
    service_name: str
    old_key: str
    expires_days: int = 90

class KeyResponse(BaseModel):
    success: bool
    api_key: Optional[str] = None
    message: str

def require_admin(user=Depends(require_auth)):
    """Require admin privileges (implement your admin check logic)"""
    # TODO: Implement proper admin role checking
    # For now, allow in LOCAL_DEV mode only
    from ..core.settings import settings
    if not settings.LOCAL_DEV:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user

@router.post("/generate", response_model=KeyResponse)
async def generate_api_key(
    request: KeyGenerateRequest,
    admin=Depends(require_admin)
):
    """Generate a new API key for a service"""
    try:
        api_key = api_key_manager.generate_api_key(
            request.service_name,
            request.expires_days
        )
        
        logger.info(f"Admin {admin['id']} generated API key for {request.service_name}")
        
        return KeyResponse(
            success=True,
            api_key=api_key,
            message=f"API key generated for {request.service_name}"
        )
    except Exception as e:
        logger.error(f"Failed to generate API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate API key"
        )

@router.post("/rotate", response_model=KeyResponse)
async def rotate_api_key(
    request: KeyRotateRequest,
    admin=Depends(require_admin)
):
    """Rotate an existing API key"""
    try:
        new_key = api_key_manager.rotate_key(
            request.service_name,
            request.old_key,
            request.expires_days
        )
        
        logger.info(f"Admin {admin['id']} rotated API key for {request.service_name}")
        
        return KeyResponse(
            success=True,
            api_key=new_key,
            message=f"API key rotated for {request.service_name}"
        )
    except Exception as e:
        logger.error(f"Failed to rotate API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to rotate API key"
        )

@router.delete("/deactivate/{key_hash}")
async def deactivate_api_key(
    key_hash: str,
    admin=Depends(require_admin)
):
    """Deactivate an API key by hash"""
    # Note: In practice, you'd need the actual key to deactivate
    # This is a simplified version for demonstration
    logger.info(f"Admin {admin['id']} requested deactivation of key {key_hash}")
    
    return {"success": True, "message": "Key deactivation requested"}

@router.get("/list")
async def list_api_keys(
    service_name: Optional[str] = None,
    admin=Depends(require_admin)
) -> List[Dict]:
    """List all API keys (without exposing actual keys)"""
    try:
        keys = api_key_manager.list_keys(service_name)
        logger.info(f"Admin {admin['id']} listed API keys for service: {service_name or 'all'}")
        return keys
    except Exception as e:
        logger.error(f"Failed to list API keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list API keys"
        )

@router.get("/rotation-schedule")
async def get_rotation_schedule(admin=Depends(require_admin)) -> List[Dict]:
    """Get keys that need rotation soon"""
    try:
        schedule = api_key_manager.get_rotation_schedule()
        logger.info(f"Admin {admin['id']} checked rotation schedule")
        return schedule
    except Exception as e:
        logger.error(f"Failed to get rotation schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get rotation schedule"
        )

@router.post("/cleanup")
async def cleanup_expired_keys(admin=Depends(require_admin)):
    """Clean up expired keys"""
    try:
        count = api_key_manager.cleanup_expired_keys()
        logger.info(f"Admin {admin['id']} cleaned up {count} expired keys")
        return {"success": True, "cleaned_up": count, "message": f"Cleaned up {count} expired keys"}
    except Exception as e:
        logger.error(f"Failed to cleanup keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cleanup expired keys"
        )
