import pytest
from jose import JWTError, jwt
from backend.src.auth.security import verify_token, create_access_token
from backend.src.core.config import settings
from datetime import datetime, timedelta


def test_jwt_token_validation_with_valid_token():
    """Test that a valid JWT token can be successfully validated"""
    # Create a valid token
    data = {"user_id": "test_user_123", "role": "user"}
    token = create_access_token(data=data)

    # Verify the token
    payload = verify_token(token)

    # Assert the payload is returned correctly
    assert payload is not None
    assert payload["user_id"] == "test_user_123"
    assert payload["role"] == "user"
    assert "exp" in payload


def test_jwt_token_validation_with_invalid_token():
    """Test that an invalid JWT token returns None"""
    # Create an invalid token (tampered with)
    invalid_token = "invalid.token.string"

    # Try to verify the token
    payload = verify_token(invalid_token)

    # Assert the payload is None
    assert payload is None


def test_jwt_token_validation_with_expired_token():
    """Test that an expired JWT token returns None"""
    # Create an expired token
    data = {"user_id": "test_user_123", "role": "user"}
    expired_token = create_access_token(data=data, expires_delta=timedelta(seconds=-1))

    # Try to verify the expired token
    payload = verify_token(expired_token)

    # Assert the payload is None
    assert payload is None


def test_jwt_token_contains_correct_claims():
    """Test that JWT tokens contain the expected claims"""
    # Create a token with specific data
    user_data = {"user_id": "test_user_456", "role": "admin", "email": "test@example.com"}
    token = create_access_token(data=user_data)

    # Decode the token without verification to check claims
    decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

    # Assert the expected claims are present
    assert decoded_payload["user_id"] == "test_user_456"
    assert decoded_payload["role"] == "admin"
    assert decoded_payload["email"] == "test@example.com"
    assert "exp" in decoded_payload


def test_jwt_algorithm_compliance():
    """Test that JWT tokens are created and validated with the correct algorithm"""
    # Create a token
    data = {"user_id": "test_user_789"}
    token = create_access_token(data=data)

    # Verify the token using the configured algorithm
    payload = verify_token(token)

    # Assert the payload is valid
    assert payload is not None
    assert payload["user_id"] == "test_user_789"


if __name__ == "__main__":
    pytest.main([__file__])