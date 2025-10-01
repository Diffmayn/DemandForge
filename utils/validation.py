"""Validation and security utilities."""
import html
from datetime import datetime, timedelta
from typing import Any, Optional
import os


def sanitize_html(text: str) -> str:
    """
    Escape HTML special characters to prevent XSS attacks.
    
    Args:
        text: Input text that may contain HTML
        
    Returns:
        Escaped text safe for display
    """
    if not isinstance(text, str):
        return str(text)
    
    return html.escape(text)


def validate_session_ttl(start_time: datetime, ttl_minutes: Optional[int] = None) -> tuple[bool, Optional[str]]:
    """
    Validate if session is still within TTL (Time To Live).
    
    Args:
        start_time: Session start timestamp
        ttl_minutes: TTL in minutes (defaults to env or 60)
        
    Returns:
        Tuple of (is_valid, warning_message)
    """
    if ttl_minutes is None:
        ttl_minutes = int(os.getenv("SESSION_TTL_MINUTES", "60"))
    
    now = datetime.now()
    elapsed = now - start_time
    ttl_delta = timedelta(minutes=ttl_minutes)
    
    if elapsed > ttl_delta:
        return False, f"Session expired after {ttl_minutes} minutes. Please refresh to start a new session."
    
    # Warning at 80% of TTL
    warning_threshold = ttl_delta * 0.8
    if elapsed > warning_threshold:
        remaining = ttl_delta - elapsed
        remaining_minutes = int(remaining.total_seconds() / 60)
        return True, f"⚠️ Session expires in {remaining_minutes} minutes. Save your work!"
    
    return True, None


def validate_input_length(text: str, max_length: int, field_name: str = "Field") -> tuple[bool, Optional[str]]:
    """
    Validate input doesn't exceed maximum length.
    
    Args:
        text: Input text
        max_length: Maximum allowed length
        field_name: Name of field for error message
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(text) > max_length:
        return False, f"{field_name} exceeds maximum length of {max_length} characters (current: {len(text)})"
    
    return True, None


def validate_list_length(items: list, max_length: int, field_name: str = "List") -> tuple[bool, Optional[str]]:
    """
    Validate list doesn't exceed maximum number of items.
    
    Args:
        items: List to validate
        max_length: Maximum allowed items
        field_name: Name of field for error message
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(items) > max_length:
        return False, f"{field_name} exceeds maximum of {max_length} items (current: {len(items)})"
    
    return True, None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks.
    
    Args:
        filename: Input filename
        
    Returns:
        Sanitized filename safe for file operations
    """
    # Remove path separators and special characters
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
    sanitized = "".join(c if c in safe_chars else "_" for c in filename)
    
    # Ensure it doesn't start with dot or dash
    if sanitized.startswith((".", "-")):
        sanitized = "file_" + sanitized
    
    # Limit length
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit(".", 1) if "." in sanitized else (sanitized, "")
        sanitized = name[:250] + ("." + ext if ext else "")
    
    return sanitized or "unnamed_file"


def check_role_access(required_role: str) -> bool:
    """
    Check if user has required role (stub for future RBAC).
    
    Args:
        required_role: Role name required for access
        
    Returns:
        True if user has access (currently always True in POC)
    """
    # Future: Integrate with Streamlit secrets or auth provider
    enable_role_check = os.getenv("ENABLE_ROLE_CHECK", "false").lower() == "true"
    
    if not enable_role_check:
        return True
    
    # Placeholder for actual role checking
    # In production: check st.session_state.user_role or st.secrets
    return True
