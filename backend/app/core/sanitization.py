"""
Input sanitization utilities for security
"""
import re
import html
import unicodedata
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

class InputSanitizer:
    """Comprehensive input sanitization for security"""
    
    # Dangerous patterns that should be blocked
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',  # JavaScript URLs
        r'vbscript:',   # VBScript URLs
        r'data:text/html',  # Data URLs with HTML
        r'onclick\s*=',  # Event handlers
        r'onerror\s*=',
        r'onload\s*=',
        r'eval\s*\(',   # eval() calls
        r'document\.',  # DOM access
        r'window\.',    # Window object access
        r'\bDROP\s+TABLE\b',  # SQL injection attempts
        r'\bUNION\s+SELECT\b',
        r'\bINSERT\s+INTO\b',
        r'\bDELETE\s+FROM\b',
        r'--\s*$',      # SQL comments
    ]
    
    @classmethod
    def sanitize_text(cls, text: Optional[str], max_length: int = 1000, allow_html: bool = False) -> str:
        """
        Sanitize text input with comprehensive security measures
        
        Args:
            text: Input text to sanitize
            max_length: Maximum allowed length
            allow_html: Whether to allow safe HTML tags
        
        Returns:
            Sanitized text string
        """
        if not text:
            return ""
        
        # Convert to string if not already
        text = str(text)
        
        # Normalize unicode characters to prevent homograph attacks
        text = unicodedata.normalize('NFKC', text)
        
        # Truncate to max length
        if len(text) > max_length:
            text = text[:max_length]
            logger.warning(f"Text truncated to {max_length} characters")
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                logger.warning(f"Dangerous pattern detected and removed: {pattern}")
                text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # HTML escape if not allowing HTML
        if not allow_html:
            text = html.escape(text)
        
        # Remove null bytes and control characters (except newlines and tabs)
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t\r')
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @classmethod
    def sanitize_filename(cls, filename: Optional[str]) -> str:
        """
        Sanitize filename to prevent path traversal and other attacks
        
        Args:
            filename: Input filename
        
        Returns:
            Safe filename
        """
        if not filename:
            return "unknown_file"
        
        filename = str(filename)
        
        # Remove path components
        filename = filename.split('/')[-1].split('\\')[-1]
        
        # Remove dangerous characters
        filename = re.sub(r'[<>:"|?*\x00-\x1f]', '_', filename)
        
        # Remove dots at the beginning (hidden files) and end
        filename = filename.strip('. ')
        
        # Ensure filename is not empty after sanitization
        if not filename:
            filename = "sanitized_file"
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:255-len(ext)-1] + '.' + ext if ext else name[:255]
        
        return filename
    
    @classmethod
    def sanitize_email(cls, email: Optional[str]) -> str:
        """
        Sanitize and validate email address
        
        Args:
            email: Input email address
        
        Returns:
            Sanitized email or empty string if invalid
        """
        if not email:
            return ""
        
        email = str(email).strip().lower()
        
        # Basic email regex validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(email_pattern, email) and len(email) <= 254:
            return email
        
        logger.warning(f"Invalid email format rejected: {email[:20]}...")
        return ""
    
    @classmethod
    def sanitize_phone(cls, phone: Optional[str]) -> str:
        """
        Sanitize phone number
        
        Args:
            phone: Input phone number
        
        Returns:
            Sanitized phone number
        """
        if not phone:
            return ""
        
        phone = str(phone)
        
        # Remove all non-digit characters except +, -, (), and spaces
        phone = re.sub(r'[^\d\+\-\(\)\s]', '', phone)
        
        # Limit length
        phone = phone[:20]
        
        return phone.strip()
    
    @classmethod
    def sanitize_policy_data(cls, data: dict) -> dict:
        """
        Sanitize all policy-related data fields
        
        Args:
            data: Dictionary of policy data
        
        Returns:
            Sanitized policy data
        """
        sanitized = {}
        
        # Text fields with specific sanitization
        text_fields = {
            'owner_name': 100,
            'insurer': 100,
            'policy_number': 50,
            'agent_name': 100,
            'notes': 2000,
            'terms_and_conditions': 10000,
        }
        
        for field, max_len in text_fields.items():
            if field in data:
                sanitized[field] = cls.sanitize_text(data[field], max_length=max_len)
        
        # Email field
        if 'contact_email' in data:
            sanitized['contact_email'] = cls.sanitize_email(data['contact_email'])
        
        # Phone field
        if 'contact_phone' in data:
            sanitized['contact_phone'] = cls.sanitize_phone(data['contact_phone'])
        
        # Filename field
        if 'original_filename' in data:
            sanitized['original_filename'] = cls.sanitize_filename(data['original_filename'])
        
        # Copy over numeric and other safe fields
        safe_fields = [
            'premium_monthly', 'premium_annual', 'deductible', 'coverage_limit',
            'start_date', 'end_date', 'product_type', 'policy_language',
            'extraction_confidence', 'pdf_file_size', 'document_type',
            'coverage_details', 'policy_chapters'
        ]
        
        for field in safe_fields:
            if field in data:
                sanitized[field] = data[field]
        
        return sanitized

# Create global instance
input_sanitizer = InputSanitizer()
