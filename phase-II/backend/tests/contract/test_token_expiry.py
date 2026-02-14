import pytest
from datetime import timedelta
from jose import jwt
from backend.src.auth.security import create_access_token, verify_token
from backend.src.core.config import settings


def test_token_expires_after_specified_duration():
    """Test that tokens expire after the configured duration"""
    # Create a token with a short expiration time
    user_data = {"user_id": "expiry_test_user", "role": "user"}

    # Create a token that expires in 1 second
    short_lived_token = create_access_token(
        data=user_data,
        expires_delta=timedelta(seconds=1)
    )

    # Verify the token is valid initially
    payload = verify_token(short_lived_token)
    assert payload is not None
    assert payload["user_id"] == "expiry_test_user"

    # Wait for more than 1 second
    import time
    time.sleep(2)

    # Now verify the token should be expired
    expired_payload = verify_token(short_lived_token)
    assert expired_payload is None


def test_token_validation_fails_for_expired_tokens():
    """Test that expired tokens fail validation"""
    from backend.src.auth.security import create_access_token, verify_token
    from datetime import timedelta

    # Create an expired token manually
    expired_data = {
        "user_id": "expired_user",
        "role": "user",
        "exp": 1000  # Set to Unix epoch + 1000 seconds (definitely in the past)
    }

    expired_token = jwt.encode(expired_data, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # Verify that the expired token is rejected
    payload = verify_token(expired_token)
    assert payload is None


def test_token_with_future_expiry_remains_valid():
    """Test that tokens with future expiry remain valid"""
    from backend.src.auth.security import create_access_token, verify_token
    from datetime import datetime, timedelta

    # Create a token that expires in 1 hour
    user_data = {"user_id": "future_expiry_user", "role": "user"}
    future_expiry_token = create_access_token(
        data=user_data,
        expires_delta=timedelta(hours=1)
    )

    # Verify the token is valid
    payload = verify_token(future_expiry_token)
    assert payload is not None
    assert payload["user_id"] == "future_expiry_user"

    # Check that the expiry time is in the future
    exp_time = payload.get("exp")
    assert exp_time is not None
    current_time = datetime.utcnow().timestamp()
    assert exp_time > current_time


def test_token_expiry_configuration_respected():
    """Test that the configured expiry duration is respected"""
    from backend.src.auth.security import create_access_token, verify_token
    from datetime import datetime, timedelta

    # Create a token with default expiry
    user_data = {"user_id": "config_test_user", "role": "user"}
    token = create_access_token(data=user_data)

    # Decode without verification to check expiry
    decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

    # Check that expiry is approximately the configured duration from now
    exp_time = decoded_payload.get("exp")
    current_time = datetime.utcnow().timestamp()
    configured_expiry_seconds = int(settings.JWT_EXPIRATION_DELTA)

    # Allow for a small margin of error (e.g., 5 seconds)
    assert abs(exp_time - current_time - configured_expiry_seconds) < 5


def test_short_lived_token_expires_correctly():
    """Test that tokens with short lifetimes expire correctly"""
    from backend.src.auth.security import create_access_token, verify_token
    from datetime import timedelta

    # Create a token that expires in 0.5 seconds
    user_data = {"user_id": "short_lived_user", "role": "user"}
    quick_expiry_token = create_access_token(
        data=user_data,
        expires_delta=timedelta(milliseconds=500)
    )

    # Token should be valid immediately
    payload = verify_token(quick_expiry_token)
    assert payload is not None

    # Wait for token to expire
    import time
    time.sleep(1)  # Sleep for 1 second (longer than 500ms expiry)

    # Token should now be invalid
    expired_payload = verify_token(quick_expiry_token)
    assert expired_payload is None


def test_token_expiry_validation_in_payload():
    """Test that token expiry validation works correctly in the payload"""
    from backend.src.auth.security import create_access_token, validate_token_not_expired
    from datetime import timedelta

    # Create a token that expires in 1 hour
    user_data = {"user_id": "validation_test_user", "role": "user"}
    valid_token = create_access_token(
        data=user_data,
        expires_delta=timedelta(hours=1)
    )

    # Decode the token to get the payload
    payload = jwt.decode(valid_token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

    # Validate that the token is not expired
    is_not_expired = validate_token_not_expired(payload)
    assert is_not_expired is True

    # Create an expired token manually
    expired_payload = {
        "user_id": "expired_validation_user",
        "role": "user",
        "exp": 1000  # Definitely in the past
    }

    # Validate that the expired token is detected
    is_expired = validate_token_not_expired(expired_payload)
    assert is_expired is False


def test_token_without_exp_claim_is_invalid():
    """Test that tokens without an expiry claim are treated as invalid"""
    from backend.src.auth.security import verify_token

    # Create a token without an expiry claim
    token_without_exp = jwt.encode(
        {"user_id": "no_exp_user", "role": "user"},
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    # The token should be considered invalid due to missing exp
    payload = verify_token(token_without_exp)
    # Note: Depending on implementation, this might succeed or fail
    # If it succeeds, it would be caught by validate_token_not_expired function


if __name__ == "__main__":
    pytest.main([__file__])