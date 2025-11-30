"""Unit tests for authentication."""

import pytest
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_access_token,
    verify_password,
    verify_refresh_token,
)
from app.core.exceptions import UnauthorizedError


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_password_hash_is_different_from_plain(self):
        """Password hash should be different from plain password."""
        password = "mysecretpassword"
        hashed = get_password_hash(password)
        assert hashed != password

    def test_verify_correct_password(self):
        """Correct password should verify successfully."""
        password = "mysecretpassword"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_incorrect_password(self):
        """Incorrect password should fail verification."""
        password = "mysecretpassword"
        hashed = get_password_hash(password)
        assert verify_password("wrongpassword", hashed) is False

    def test_same_password_different_hashes(self):
        """Same password should produce different hashes (salt)."""
        password = "mysecretpassword"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2
        # But both should verify
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """Tests for JWT token functions."""

    def test_create_access_token(self):
        """Access token should be created successfully."""
        token = create_access_token(subject="user123")
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self):
        """Refresh token should be created successfully."""
        token = create_refresh_token(subject="user123")
        assert token is not None
        assert isinstance(token, str)

    def test_verify_valid_access_token(self):
        """Valid access token should verify successfully."""
        token = create_access_token(subject="user123")
        payload = verify_access_token(token)
        assert payload["sub"] == "user123"
        assert payload["type"] == "access"

    def test_verify_valid_refresh_token(self):
        """Valid refresh token should verify successfully."""
        token = create_refresh_token(subject="user123")
        payload = verify_refresh_token(token)
        assert payload["sub"] == "user123"
        assert payload["type"] == "refresh"

    def test_access_token_with_additional_claims(self):
        """Access token should include additional claims."""
        token = create_access_token(
            subject="user123",
            additional_claims={"email": "test@example.com", "role": "ADMIN"},
        )
        payload = verify_access_token(token)
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "ADMIN"

    def test_verify_invalid_token(self):
        """Invalid token should raise UnauthorizedError."""
        with pytest.raises(UnauthorizedError):
            verify_access_token("invalid.token.here")

    def test_access_token_fails_refresh_verification(self):
        """Access token should fail refresh token verification."""
        token = create_access_token(subject="user123")
        with pytest.raises(UnauthorizedError):
            verify_refresh_token(token)

    def test_refresh_token_fails_access_verification(self):
        """Refresh token should fail access token verification."""
        token = create_refresh_token(subject="user123")
        with pytest.raises(UnauthorizedError):
            verify_access_token(token)
