"""
API Key rotation and management system
"""
import os
import json
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging
from cryptography.fernet import Fernet
from ..core.settings import settings

logger = logging.getLogger(__name__)

class APIKeyManager:
    """Secure API key rotation and management"""
    
    def __init__(self, storage_path: str = "api_keys.enc"):
        self.storage_path = Path(storage_path)
        self.encryption_key = self._get_or_create_encryption_key()
        self.fernet = Fernet(self.encryption_key)
        
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for API key storage"""
        key_file = Path("api_key_encryption.key")
        
        if key_file.exists():
            with open(key_file, "rb") as f:
                return f.read()
        else:
            # Generate new encryption key
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            # Make file readable only by owner
            os.chmod(key_file, 0o600)
            return key
    
    def _load_keys(self) -> Dict:
        """Load encrypted API keys from storage"""
        if not self.storage_path.exists():
            return {}
        
        try:
            with open(self.storage_path, "rb") as f:
                encrypted_data = f.read()
            
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            logger.error(f"Failed to load API keys: {e}")
            return {}
    
    def _save_keys(self, keys: Dict) -> None:
        """Save encrypted API keys to storage"""
        try:
            json_data = json.dumps(keys, indent=2)
            encrypted_data = self.fernet.encrypt(json_data.encode())
            
            with open(self.storage_path, "wb") as f:
                f.write(encrypted_data)
            
            # Make file readable only by owner
            os.chmod(self.storage_path, 0o600)
        except Exception as e:
            logger.error(f"Failed to save API keys: {e}")
            raise
    
    def generate_api_key(self, service_name: str, expires_days: int = 90) -> str:
        """
        Generate a new API key for a service
        
        Args:
            service_name: Name of the service (e.g., 'openai', 'insurer_api')
            expires_days: Number of days until expiration
        
        Returns:
            New API key
        """
        # Generate secure random key
        api_key = secrets.token_urlsafe(32)
        
        # Create key metadata
        key_data = {
            "key": api_key,
            "service": service_name,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=expires_days)).isoformat(),
            "is_active": True,
            "usage_count": 0,
            "last_used": None
        }
        
        # Load existing keys
        keys = self._load_keys()
        
        # Store new key with hash as identifier
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
        keys[key_hash] = key_data
        
        # Save updated keys
        self._save_keys(keys)
        
        logger.info(f"Generated new API key for {service_name} (expires in {expires_days} days)")
        return api_key
    
    def rotate_key(self, service_name: str, old_key: str, expires_days: int = 90) -> str:
        """
        Rotate an existing API key
        
        Args:
            service_name: Name of the service
            old_key: Current API key to rotate
            expires_days: Number of days until new key expires
        
        Returns:
            New API key
        """
        # Deactivate old key
        self.deactivate_key(old_key)
        
        # Generate new key
        new_key = self.generate_api_key(service_name, expires_days)
        
        logger.info(f"Rotated API key for {service_name}")
        return new_key
    
    def deactivate_key(self, api_key: str) -> bool:
        """
        Deactivate an API key
        
        Args:
            api_key: API key to deactivate
        
        Returns:
            True if key was found and deactivated
        """
        keys = self._load_keys()
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
        
        if key_hash in keys:
            keys[key_hash]["is_active"] = False
            keys[key_hash]["deactivated_at"] = datetime.utcnow().isoformat()
            self._save_keys(keys)
            logger.info(f"Deactivated API key for {keys[key_hash]['service']}")
            return True
        
        return False
    
    def validate_key(self, api_key: str) -> Tuple[bool, Optional[Dict]]:
        """
        Validate an API key
        
        Args:
            api_key: API key to validate
        
        Returns:
            Tuple of (is_valid, key_metadata)
        """
        keys = self._load_keys()
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
        
        if key_hash not in keys:
            return False, None
        
        key_data = keys[key_hash]
        
        # Check if key is active
        if not key_data.get("is_active", False):
            return False, key_data
        
        # Check if key is expired
        expires_at = datetime.fromisoformat(key_data["expires_at"])
        if datetime.utcnow() > expires_at:
            # Auto-deactivate expired key
            key_data["is_active"] = False
            key_data["expired_at"] = datetime.utcnow().isoformat()
            keys[key_hash] = key_data
            self._save_keys(keys)
            return False, key_data
        
        # Update usage stats
        key_data["usage_count"] = key_data.get("usage_count", 0) + 1
        key_data["last_used"] = datetime.utcnow().isoformat()
        keys[key_hash] = key_data
        self._save_keys(keys)
        
        return True, key_data
    
    def list_keys(self, service_name: Optional[str] = None) -> List[Dict]:
        """
        List all API keys, optionally filtered by service
        
        Args:
            service_name: Optional service name filter
        
        Returns:
            List of key metadata (without actual keys)
        """
        keys = self._load_keys()
        result = []
        
        for key_hash, key_data in keys.items():
            if service_name and key_data.get("service") != service_name:
                continue
            
            # Don't include actual key in listing
            safe_data = {k: v for k, v in key_data.items() if k != "key"}
            safe_data["key_hash"] = key_hash
            result.append(safe_data)
        
        return result
    
    def cleanup_expired_keys(self) -> int:
        """
        Remove expired keys older than 30 days
        
        Returns:
            Number of keys cleaned up
        """
        keys = self._load_keys()
        cleanup_threshold = datetime.utcnow() - timedelta(days=30)
        
        keys_to_remove = []
        for key_hash, key_data in keys.items():
            if not key_data.get("is_active", False):
                # Check if key was deactivated or expired more than 30 days ago
                deactivated_at = key_data.get("deactivated_at") or key_data.get("expired_at")
                if deactivated_at:
                    deactivated_time = datetime.fromisoformat(deactivated_at)
                    if deactivated_time < cleanup_threshold:
                        keys_to_remove.append(key_hash)
        
        # Remove old keys
        for key_hash in keys_to_remove:
            del keys[key_hash]
        
        if keys_to_remove:
            self._save_keys(keys)
            logger.info(f"Cleaned up {len(keys_to_remove)} expired API keys")
        
        return len(keys_to_remove)
    
    def get_rotation_schedule(self) -> List[Dict]:
        """
        Get keys that need rotation (expiring within 7 days)
        
        Returns:
            List of keys needing rotation
        """
        keys = self._load_keys()
        rotation_threshold = datetime.utcnow() + timedelta(days=7)
        
        needs_rotation = []
        for key_hash, key_data in keys.items():
            if not key_data.get("is_active", False):
                continue
            
            expires_at = datetime.fromisoformat(key_data["expires_at"])
            if expires_at <= rotation_threshold:
                safe_data = {k: v for k, v in key_data.items() if k != "key"}
                safe_data["key_hash"] = key_hash
                safe_data["days_until_expiry"] = (expires_at - datetime.utcnow()).days
                needs_rotation.append(safe_data)
        
        return needs_rotation

# Global instance
api_key_manager = APIKeyManager()
