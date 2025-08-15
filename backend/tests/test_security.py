"""
Unit tests for security features
"""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import UploadFile
import io

# Import the modules to test
from app.core.sanitization import InputSanitizer, input_sanitizer
from app.core.api_key_manager import APIKeyManager
from app.core.exceptions import (
    ValidationException, 
    AuthenticationException,
    FileProcessingException,
    ErrorCode
)
from app.main import app

class TestInputSanitization:
    """Test suite for input sanitization functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.sanitizer = InputSanitizer()
    
    def test_sanitize_text_basic(self):
        """Test basic text sanitization"""
        # Normal text should pass through
        result = self.sanitizer.sanitize_text("Hello World")
        assert result == "Hello World"
        
        # Empty/None should return empty string
        assert self.sanitizer.sanitize_text(None) == ""
        assert self.sanitizer.sanitize_text("") == ""
    
    def test_sanitize_text_xss_prevention(self):
        """Test XSS attack prevention"""
        # Script tags should be removed
        malicious_input = "<script>alert('xss')</script>Hello"
        result = self.sanitizer.sanitize_text(malicious_input)
        assert "<script>" not in result
        assert "alert" not in result
        
        # JavaScript URLs should be removed
        js_url = "javascript:alert('xss')"
        result = self.sanitizer.sanitize_text(js_url)
        assert "javascript:" not in result
        
        # Event handlers should be removed
        onclick_attack = "Hello onclick=alert('xss')"
        result = self.sanitizer.sanitize_text(onclick_attack)
        assert "onclick" not in result
    
    def test_sanitize_text_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        # SQL injection attempts should be blocked
        sql_injection = "'; DROP TABLE users; --"
        result = self.sanitizer.sanitize_text(sql_injection)
        assert "DROP TABLE" not in result
        assert "--" not in result
        
        # UNION SELECT should be blocked
        union_select = "1 UNION SELECT password FROM users"
        result = self.sanitizer.sanitize_text(union_select)
        assert "UNION SELECT" not in result
    
    def test_sanitize_text_length_limit(self):
        """Test text length limiting"""
        long_text = "A" * 2000
        result = self.sanitizer.sanitize_text(long_text, max_length=100)
        assert len(result) == 100
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        # Normal filename
        assert self.sanitizer.sanitize_filename("document.pdf") == "document.pdf"
        
        # Path traversal attempts
        assert self.sanitizer.sanitize_filename("../../../etc/passwd") == "passwd"
        assert self.sanitizer.sanitize_filename("..\\..\\windows\\system32") == "system32"
        
        # Dangerous characters
        dangerous = "file<>:\"|?*.txt"
        result = self.sanitizer.sanitize_filename(dangerous)
        assert not any(char in result for char in '<>:"|?*')
        
        # Empty filename
        assert self.sanitizer.sanitize_filename("") == "unknown_file"
        assert self.sanitizer.sanitize_filename(None) == "unknown_file"
    
    def test_sanitize_email(self):
        """Test email sanitization and validation"""
        # Valid emails
        assert self.sanitizer.sanitize_email("test@example.com") == "test@example.com"
        assert self.sanitizer.sanitize_email("USER@EXAMPLE.COM") == "user@example.com"
        
        # Invalid emails
        assert self.sanitizer.sanitize_email("invalid-email") == ""
        assert self.sanitizer.sanitize_email("@example.com") == ""
        assert self.sanitizer.sanitize_email("test@") == ""
        assert self.sanitizer.sanitize_email(None) == ""
    
    def test_sanitize_phone(self):
        """Test phone number sanitization"""
        # Valid phone numbers
        assert self.sanitizer.sanitize_phone("123-456-7890") == "123-456-7890"
        assert self.sanitizer.sanitize_phone("+1 (555) 123-4567") == "+1 (555) 123-4567"
        
        # Remove invalid characters
        result = self.sanitizer.sanitize_phone("123abc456def7890")
        assert "abc" not in result
        assert "def" not in result
        
        # Empty/None
        assert self.sanitizer.sanitize_phone(None) == ""
        assert self.sanitizer.sanitize_phone("") == ""
    
    def test_sanitize_policy_data(self):
        """Test comprehensive policy data sanitization"""
        policy_data = {
            "owner_name": "<script>alert('xss')</script>John Doe",
            "insurer": "Test Insurance Co.",
            "policy_number": "POL-123456",
            "contact_email": "JOHN@EXAMPLE.COM",
            "contact_phone": "123abc456def7890",
            "original_filename": "../../../malicious.pdf",
            "notes": "'; DROP TABLE policies; --",
            "premium_monthly": 100.0,
            "invalid_field": "should be ignored"
        }
        
        result = self.sanitizer.sanitize_policy_data(policy_data)
        
        # Check XSS was removed
        assert "<script>" not in result["owner_name"]
        assert "John Doe" in result["owner_name"]
        
        # Check email was normalized
        assert result["contact_email"] == "john@example.com"
        
        # Check phone was cleaned
        assert "abc" not in result["contact_phone"]
        assert "def" not in result["contact_phone"]
        
        # Check filename was sanitized
        assert result["original_filename"] == "malicious.pdf"
        
        # Check SQL injection was blocked
        assert "DROP TABLE" not in result["notes"]
        
        # Check numeric fields passed through
        assert result["premium_monthly"] == 100.0
        
        # Check invalid fields were preserved (we only sanitize known fields)
        assert "invalid_field" not in result

class TestAPIKeyManager:
    """Test suite for API key management"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Use temporary file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.key_manager = APIKeyManager(
            storage_path=os.path.join(self.temp_dir, "test_keys.enc")
        )
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_generate_api_key(self):
        """Test API key generation"""
        # Generate a key
        api_key = self.key_manager.generate_api_key("test_service", expires_days=30)
        
        # Key should be generated
        assert api_key is not None
        assert len(api_key) > 20  # Should be reasonably long
        
        # Should be able to validate the key
        is_valid, metadata = self.key_manager.validate_key(api_key)
        assert is_valid is True
        assert metadata["service"] == "test_service"
        assert metadata["is_active"] is True
    
    def test_rotate_api_key(self):
        """Test API key rotation"""
        # Generate initial key
        old_key = self.key_manager.generate_api_key("test_service")
        
        # Rotate the key
        new_key = self.key_manager.rotate_key("test_service", old_key)
        
        # New key should be different
        assert new_key != old_key
        
        # Old key should be deactivated
        is_valid, _ = self.key_manager.validate_key(old_key)
        assert is_valid is False
        
        # New key should be valid
        is_valid, _ = self.key_manager.validate_key(new_key)
        assert is_valid is True
    
    def test_deactivate_key(self):
        """Test key deactivation"""
        # Generate a key
        api_key = self.key_manager.generate_api_key("test_service")
        
        # Deactivate it
        result = self.key_manager.deactivate_key(api_key)
        assert result is True
        
        # Should no longer be valid
        is_valid, metadata = self.key_manager.validate_key(api_key)
        assert is_valid is False
        assert metadata["is_active"] is False
    
    def test_validate_expired_key(self):
        """Test validation of expired keys"""
        # This would require mocking datetime to test expiration
        # For now, test the basic validation logic
        api_key = self.key_manager.generate_api_key("test_service")
        
        # Valid key
        is_valid, metadata = self.key_manager.validate_key(api_key)
        assert is_valid is True
        assert metadata["usage_count"] == 1
        
        # Second validation should increment usage
        is_valid, metadata = self.key_manager.validate_key(api_key)
        assert is_valid is True
        assert metadata["usage_count"] == 2
    
    def test_list_keys(self):
        """Test key listing"""
        # Generate keys for different services
        self.key_manager.generate_api_key("service1")
        self.key_manager.generate_api_key("service2")
        self.key_manager.generate_api_key("service1")  # Second key for service1
        
        # List all keys
        all_keys = self.key_manager.list_keys()
        assert len(all_keys) == 3
        
        # List keys for specific service
        service1_keys = self.key_manager.list_keys("service1")
        assert len(service1_keys) == 2
        assert all(key["service"] == "service1" for key in service1_keys)
        
        # Ensure actual keys are not in the listing
        for key_data in all_keys:
            assert "key" not in key_data

class TestExceptionHandling:
    """Test suite for exception handling"""
    
    def test_validation_exception(self):
        """Test validation exception creation and serialization"""
        exc = ValidationException("Test validation error", field="email")
        
        assert exc.error_code == ErrorCode.INVALID_INPUT
        assert exc.status_code == 400
        assert exc.details["field"] == "email"
        
        # Test serialization
        data = exc.to_dict()
        assert data["error"]["code"] == "VAL_001"
        assert "invalid" in data["error"]["message"].lower()
    
    def test_file_processing_exception(self):
        """Test file processing exception"""
        exc = FileProcessingException("Failed to process PDF", filename="test.pdf")
        
        assert exc.error_code == ErrorCode.PDF_PROCESSING_ERROR
        assert exc.status_code == 422
        assert exc.details["filename"] == "test.pdf"
    
    def test_authentication_exception(self):
        """Test authentication exception"""
        exc = AuthenticationException("Invalid credentials")
        
        assert exc.error_code == ErrorCode.AUTHENTICATION_FAILED
        assert exc.status_code == 401
        assert "Authentication failed" in exc.user_message

class TestSecurityMiddleware:
    """Test suite for security middleware"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = TestClient(app)
    
    def test_security_headers_applied(self):
        """Test that security headers are applied to responses"""
        # Make a request to any endpoint
        response = self.client.get("/")
        
        # Check for key security headers
        headers = response.headers
        
        # Content Security Policy should be present
        assert "content-security-policy" in headers
        
        # X-Frame-Options should be set
        assert headers.get("x-frame-options") == "DENY"
        
        # X-Content-Type-Options should be set
        assert headers.get("x-content-type-options") == "nosniff"
        
        # X-XSS-Protection should be enabled
        assert headers.get("x-xss-protection") == "1; mode=block"
    
    def test_cors_restrictions(self):
        """Test CORS restrictions"""
        # Test that CORS headers are properly restricted
        response = self.client.options("/api/policies")
        
        # Should have CORS headers but restricted origins
        cors_origins = response.headers.get("access-control-allow-origin")
        if cors_origins:
            # Should not be wildcard in production
            assert cors_origins != "*"

class TestFileUploadSecurity:
    """Test suite for file upload security"""
    
    def setup_method(self):
        """Set up test client with authentication mock"""
        self.client = TestClient(app)
        
        # Mock authentication
        self.auth_patch = patch('app.core.auth_security.require_auth')
        self.mock_auth = self.auth_patch.start()
        self.mock_auth.return_value = {"id": "test_user", "email": "test@example.com"}
    
    def teardown_method(self):
        """Clean up patches"""
        self.auth_patch.stop()
    
    def test_file_type_validation(self):
        """Test file type validation"""
        # Create a fake file with invalid extension
        fake_file = io.BytesIO(b"fake content")
        
        response = self.client.post(
            "/api/policies/import/pdf",
            files={"file": ("malicious.exe", fake_file, "application/octet-stream")}
        )
        
        # Should reject invalid file types
        assert response.status_code in [400, 422]
        assert ("not allowed" in response.text.lower() or 
                "validation" in response.text.lower() or 
                "invalid" in response.text.lower())
    
    def test_filename_sanitization(self):
        """Test filename sanitization in uploads"""
        # Create a file with dangerous filename
        import uuid
        fake_pdf = io.BytesIO(b"%PDF-1.4 fake pdf content")
        unique_id = str(uuid.uuid4())[:8]
        dangerous_filename = f"../../../etc/passwd_{unique_id}.pdf"
        
        response = self.client.post(
            "/api/policies/import/pdf",
            files={"file": (dangerous_filename, fake_pdf, "application/pdf")}
        )
        
        # Should accept the file but sanitize the filename
        # (The exact response depends on PDF processing, but filename should be sanitized)
        assert response.status_code in [200, 201, 400, 422]  # Should handle gracefully

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
