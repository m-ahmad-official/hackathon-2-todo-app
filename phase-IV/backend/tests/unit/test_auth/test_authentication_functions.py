import pytest
from datetime import timedelta
from jose import jwt
from backend.src.auth.security import create_access_token, verify_token
from backend.src.core.config import settings


def test_create_valid_jwt_token():
    """Test that creating a JWT token works correctly"""
    user_data = {"user_id": "test_user_123", "role": "user"}

    token = create_access_token(data=user_data)

    # Verify the token was created
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0

    # Verify the token can be decoded
    decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    assert decoded_payload["user_id"] == "test_user_123"
    assert decoded_payload["role"] == "user"
    assert "exp" in decoded_payload


def test_create_token_with_custom_expiry():
    """Test that creating a token with custom expiry works"""
    user_data = {"user_id": "expiry_test_user", "role": "user"}
    expiry_delta = timedelta(minutes=30)

    token = create_access_token(data=user_data, expires_delta=expiry_delta)

    # Decode the token without verification to check expiry
    decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

    # Check that expiry is approximately 30 minutes from now
    import time
    current_time = time.time()
    exp_time = decoded_payload["exp"]

    # Should be approximately 30 minutes (1800 seconds) from now
    assert abs(exp_time - current_time - 1800) < 10  # Allow 10 second tolerance


def test_verify_valid_token():
    """Test that verifying a valid token returns the correct payload"""
    user_data = {"user_id": "verify_test_user", "role": "admin"}
    token = create_access_token(data=user_data)

    payload = verify_token(token)

    assert payload is not None
    assert payload["user_id"] == "verify_test_user"
    assert payload["role"] == "admin"


def test_verify_invalid_token():
    """Test that verifying an invalid token returns None"""
    invalid_token = "this.is.not.a.valid.jwt.token"

    payload = verify_token(invalid_token)

    assert payload is None


def test_verify_expired_token():
    """Test that verifying an expired token returns None"""
    user_data = {"user_id": "expired_test_user", "role": "user"}
    # Create a token that expires immediately
    token = create_access_token(data=user_data, expires_delta=timedelta(seconds=-1))

    payload = verify_token(token)

    assert payload is None


def test_verify_token_with_different_secret():
    """Test that verifying a token with wrong secret returns None"""
    user_data = {"user_id": "wrong_secret_user", "role": "user"}
    token = create_access_token(data=user_data)

    # Try to verify with a different secret
    different_secret = "different_secret_key_that_does_not_match"
    try:
        payload = jwt.decode(token, different_secret, algorithms=[settings.JWT_ALGORITHM])
        # If this doesn't raise an exception, the payload should be invalid
        assert False, "Expected JWTError was not raised"
    except jwt.JWTError:
        # Expected behavior - token should not be valid with different secret
        pass


def test_token_contains_correct_claims():
    """Test that tokens contain the expected claims"""
    user_data = {
        "user_id": "claims_test_user",
        "role": "tester",
        "email": "test@example.com",
        "custom_field": "custom_value"
    }
    token = create_access_token(data=user_data)

    decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

    # Check that all original data is preserved
    assert decoded_payload["user_id"] == "claims_test_user"
    assert decoded_payload["role"] == "tester"
    assert decoded_payload["email"] == "test@example.com"
    assert decoded_payload["custom_field"] == "custom_value"

    # Check that expiration is added
    assert "exp" in decoded_payload


def test_token_algorithm_compliance():
    """Test that tokens are created and verified with the configured algorithm"""
    user_data = {"user_id": "algorithm_test_user", "role": "user"}
    token = create_access_token(data=user_data)

    # Verify using the configured algorithm
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

    assert payload["user_id"] == "algorithm_test_user"


def test_empty_user_data_token():
    """Test creating and verifying a token with minimal data"""
    user_data = {}  # Empty dictionary
    token = create_access_token(data=user_data)

    payload = verify_token(token)

    # Should contain expiration but no other claims
    assert payload is not None
    assert "exp" in payload


def test_large_user_data_token():
    """Test creating and verifying a token with large data payload"""
    large_data = {"user_id": "large_data_user", "data": "x" * 1000}  # Large string
    token = create_access_token(data=large_data)

    payload = verify_token(token)

    assert payload is not None
    assert payload["user_id"] == "large_data_user"
    assert len(payload["data"]) == 1000


def test_token_unicode_support():
    """Test that tokens handle Unicode characters correctly"""
    unicode_data = {"user_id": "用户测试", "name": "José María", "role": "测试角色"}
    token = create_access_token(data=unicode_data)

    payload = verify_token(token)

    assert payload is not None
    assert payload["user_id"] == "用户测试"
    assert payload["name"] == "José María"
    assert payload["role"] == "测试角色"


def test_concurrent_token_creation():
    """Test that multiple tokens can be created concurrently without issues"""
    import threading
    import time

    results = []

    def create_token_and_store(index):
        user_data = {"user_id": f"concurrent_user_{index}", "role": "user"}
        token = create_access_token(data=user_data)
        payload = verify_token(token)
        results.append((index, token, payload))

    # Create 5 tokens in parallel
    threads = []
    for i in range(5):
        thread = threading.Thread(target=create_token_and_store, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify all tokens were created and verified correctly
    assert len(results) == 5
    for index, token, payload in results:
        assert token is not None
        assert payload is not None
        assert payload["user_id"] == f"concurrent_user_{index}"


if __name__ == "__main__":
    pytest.main([__file__])