"""Tests for validation utilities."""
import pytest
from datetime import datetime, timedelta
from utils.validation import (
    sanitize_html,
    validate_session_ttl,
    validate_input_length,
    validate_list_length,
    sanitize_filename,
    check_role_access
)


class TestSanitizeHtml:
    """Test HTML sanitization."""
    
    def test_sanitize_basic_html(self):
        """Test basic HTML escaping."""
        input_text = "<script>alert('xss')</script>"
        result = sanitize_html(input_text)
        
        assert "<script>" not in result
        assert "&lt;script&gt;" in result
    
    def test_sanitize_quotes(self):
        """Test quote escaping."""
        input_text = 'He said "hello"'
        result = sanitize_html(input_text)
        
        assert "&quot;" in result or '"' in result
    
    def test_sanitize_ampersand(self):
        """Test ampersand escaping."""
        input_text = "Fish & Chips"
        result = sanitize_html(input_text)
        
        assert "&amp;" in result
    
    def test_sanitize_non_string(self):
        """Test handling non-string input."""
        result = sanitize_html(123)
        assert result == "123"


class TestValidateSessionTtl:
    """Test session TTL validation."""
    
    def test_valid_session(self):
        """Test session within TTL."""
        start_time = datetime.now() - timedelta(minutes=10)
        is_valid, warning = validate_session_ttl(start_time, ttl_minutes=60)
        
        assert is_valid is True
        assert warning is None
    
    def test_expired_session(self):
        """Test expired session."""
        start_time = datetime.now() - timedelta(minutes=70)
        is_valid, warning = validate_session_ttl(start_time, ttl_minutes=60)
        
        assert is_valid is False
        assert warning is not None
        assert "expired" in warning.lower()
    
    def test_warning_threshold(self):
        """Test warning at 80% TTL."""
        start_time = datetime.now() - timedelta(minutes=50)
        is_valid, warning = validate_session_ttl(start_time, ttl_minutes=60)
        
        assert is_valid is True
        assert warning is not None
        assert "expires" in warning.lower()


class TestValidateInputLength:
    """Test input length validation."""
    
    def test_valid_length(self):
        """Test input within limits."""
        text = "Short text"
        is_valid, error = validate_input_length(text, 100, "Test Field")
        
        assert is_valid is True
        assert error is None
    
    def test_exceeds_length(self):
        """Test input exceeding limits."""
        text = "x" * 200
        is_valid, error = validate_input_length(text, 100, "Test Field")
        
        assert is_valid is False
        assert error is not None
        assert "exceeds" in error.lower()
        assert "100" in error


class TestValidateListLength:
    """Test list length validation."""
    
    def test_valid_list(self):
        """Test list within limits."""
        items = [1, 2, 3]
        is_valid, error = validate_list_length(items, 10, "Test List")
        
        assert is_valid is True
        assert error is None
    
    def test_exceeds_list_length(self):
        """Test list exceeding limits."""
        items = list(range(20))
        is_valid, error = validate_list_length(items, 10, "Test List")
        
        assert is_valid is False
        assert error is not None
        assert "10" in error


class TestSanitizeFilename:
    """Test filename sanitization."""
    
    def test_safe_filename(self):
        """Test already safe filename."""
        filename = "document_2025.pdf"
        result = sanitize_filename(filename)
        
        assert result == "document_2025.pdf"
    
    def test_path_traversal_attempt(self):
        """Test prevention of path traversal."""
        filename = "../../etc/passwd"
        result = sanitize_filename(filename)
        
        assert ".." not in result
        assert "/" not in result
    
    def test_special_characters(self):
        """Test removal of special characters."""
        filename = "my<file>name?.txt"
        result = sanitize_filename(filename)
        
        assert "<" not in result
        assert ">" not in result
        assert "?" not in result
    
    def test_long_filename(self):
        """Test truncation of long filenames."""
        filename = "x" * 300 + ".txt"
        result = sanitize_filename(filename)
        
        assert len(result) <= 255
        assert result.endswith(".txt")
    
    def test_empty_filename(self):
        """Test handling of empty filename."""
        filename = ""
        result = sanitize_filename(filename)
        
        assert result == "unnamed_file"


class TestCheckRoleAccess:
    """Test role-based access control."""
    
    def test_access_allowed_default(self):
        """Test access allowed by default."""
        result = check_role_access("admin")
        
        assert result is True
    
    def test_various_roles(self):
        """Test different role names."""
        roles = ["BA", "PO", "Developer", "QA", "Admin"]
        
        for role in roles:
            assert check_role_access(role) is True
