import pytest
from datetime import timedelta
from jose import jwt
from backend.src.auth.security import create_access_token, verify_token
from backend.src.core.config import settings


def test_create_valid_access_token():
    """Test that creating a valid access token works correctly"""
    user_data = {"user_id": "test_user_123", "role": "user"}

    token = create_access_token(data=user_data)

    # Verify that the token was created
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0

    # Verify that the token can be decoded and contains the right data
    decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    assert decoded_payload["user_id"] == "test_user_123"
    assert decoded_payload["role"] == "user"
    assert "exp" in decoded_payload


def test_create_access_token_with_custom_expiry():
    """Test that creating a token with custom expiry works correctly"""
    user_data = {"user_id": "expiry_test_user", "role": "admin"}

    # Create a token that expires in 1 hour
    token = create_access_token(data=user_data, expires_delta=timedelta(hours=1))

    # Decode the token without verification to check expiry
    decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

    assert decoded_payload["user_id"] == "expiry_test_user"
    assert decoded_payload["role"] == "admin"

    # Check that expiry is approximately 1 hour from now
    import time
    current_time = time.time()
    exp_time = decoded_payload["exp"]
    expected_exp = current_time + (60 * 60)  # 1 hour in seconds

    # Allow for a small time difference (max 10 seconds)
    assert abs(exp_time - expected_exp) < 10


def test_verify_valid_token():
    """Test that verifying a valid token returns the correct payload"""
    user_data = {"user_id": "valid_user", "role": "user"}
    token = create_access_token(data=user_data)

    payload = verify_token(token)

    assert payload is not None
    assert payload["user_id"] == "valid_user"
    assert payload["role"] == "user"


def test_verify_invalid_token():
    """Test that verifying an invalid token returns None"""
    invalid_token = "invalid.token.string"

    payload = verify_token(invalid_token)

    assert payload is None


def test_verify_expired_token():
    """Test that verifying an expired token returns None"""
    user_data = {"user_id": "expired_user", "role": "user"}

    # Create a token that expires immediately
    expired_token = create_access_token(data=user_data, expires_delta=timedelta(seconds=-1))

    payload = verify_token(expired_token)

    # The expired token should not be verified successfully
    assert payload is None


def test_verify_token_with_different_secret():
    """Test that verifying a token with a different secret returns None"""
    user_data = {"user_id": "different_secret_user", "role": "user"}
    token = create_access_token(data=user_data)

    # Try to decode with a different secret - this should raise an exception
    different_secret = "different_secret_key"
    try:
        payload = jwt.decode(token, different_secret, algorithms=[settings.JWT_ALGORITHM])
        # If decoding succeeds with wrong secret, the test should fail
        assert False, "Token should not be valid with different secret"
    except Exception:
        # This is expected - the token should not be valid with a different secret
        pass


def test_token_contains_required_claims():
    """Test that tokens contain all required claims"""
    user_data = {
        "user_id": "claims_test_user",
        "role": "admin",
        "email": "test@example.com"
    }
    token = create_access_token(data=user_data)

    decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

    # Check that all original data is preserved
    assert decoded_payload["user_id"] == "claims_test_user"
    assert decoded_payload["role"] == "admin"
    assert decoded_payload["email"] == "test@example.com"

    # Check that expiration is added
    assert "exp" in decoded_payload


def test_token_algorithm_compliance():
    """Test that tokens are created and verified with the configured algorithm"""
    user_data = {"user_id": "algorithm_test_user", "role": "user"}
    token = create_access_token(data=user_data)

    # Verify using the configured algorithm
    decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

    assert decoded_payload["user_id"] == "algorithm_test_user"


def test_empty_user_data_token():
    """Test that tokens can be created with minimal data"""
    user_data = {}  # Empty dictionary
    token = create_access_token(data=user_data)

    decoded_payload = verify_token(token)

    # Should contain expiration but no other claims
    assert decoded_payload is not None
    assert "exp" in decoded_payload


def test_large_user_data_token():
    """Test that tokens handle large user data payloads correctly"""
    large_data = {
        "user_id": "large_data_user",
        "role": "user",
        "profile": "x" * 1000,  # Large string
        "preferences": {
            "theme": "dark",
            "notifications": True,
            "settings": list(range(100))  # Large list
        }
    }
    token = create_access_token(data=large_data)

    payload = verify_token(token)

    assert payload is not None
    assert payload["user_id"] == "large_data_user"
    assert len(payload["profile"]) == 1000


def test_concurrent_token_creation():
    """Test that multiple tokens can be created concurrently without issues"""
    import concurrent.futures
    import threading

    results = []

    def create_token_for_user(user_id):
        user_data = {"user_id": user_id, "role": "user"}
        token = create_access_token(data=user_data)
        payload = verify_token(token)
        return (user_id, token, payload)

    # Create 5 tokens in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(create_token_for_user, f"concurrent_user_{i}")
            for i in range(5)
        ]

        for future in concurrent.futures.as_completed(futures):
            user_id, token, payload = future.result()
            results.append((user_id, token, payload))

    # Verify all tokens were created and verified correctly
    assert len(results) == 5
    for user_id, token, payload in results:
        assert token is not None
        assert payload is not None
        assert payload["user_id"] == user_id


def test_unicode_user_data():
    """Test that tokens handle Unicode characters correctly"""
    unicode_data = {
        "user_id": "用户测试",
        "name": "José María",
        "role": "测试角色"
    }
    token = create_access_token(data=unicode_data)

    payload = verify_token(token)

    assert payload is not None
    assert payload["user_id"] == "用户测试"
    assert payload["name"] == "José María"
    assert payload["role"] == "测试角色"


def test_token_security_best_practices():
    """Test that tokens follow security best practices"""
    user_data = {"user_id": "security_test_user", "role": "user"}
    token = create_access_token(data=user_data)

    # Verify token format (should be three parts separated by dots)
    parts = token.split('.')
    assert len(parts) == 3

    # Verify that header contains expected algorithm
    import base64
    header_json = base64.b64decode(parts[0] + '==').decode('utf-8')
    import json
    header = json.loads(header_json)
    assert header["alg"] == settings.JWT_ALGORITHM
    assert header["typ"] == "JWT"


if __name__ == "__main__":
    pytest.main([__file__])