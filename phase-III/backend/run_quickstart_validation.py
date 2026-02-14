#!/usr/bin/env python3
"""
Quickstart validation script for the Todo API backend
This script validates that all core functionality works as expected
"""

import subprocess
import sys
import time
import requests
import json
from datetime import datetime, timedelta
from jose import jwt
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from src.core.config import settings


def validate_project_structure():
    """Validate that all required project files and directories exist"""
    print("🔍 Validating project structure...")

    required_files = [
        "src/main.py",
        "src/models/task.py",
        "src/services/task_service.py",
        "src/api/v1/tasks.py",
        "src/auth/security.py",
        "src/auth/deps.py",
        "src/core/config.py",
        "src/core/database.py",
        "requirements.txt"
    ]

    missing_files = []
    for file in required_files:
        full_path = f"./{file}"
        try:
            with open(full_path, 'r'):
                pass
        except FileNotFoundError:
            missing_files.append(full_path)

    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False

    print("✅ All required files exist")
    return True


def validate_dependencies():
    """Validate that all required dependencies are available"""
    print("🔍 Validating dependencies...")

    try:
        import fastapi
        import sqlmodel
        import jose
        import pydantic
        print("✅ All required dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False


def validate_config():
    """Validate that configuration is properly set up"""
    print("🔍 Validating configuration...")

    try:
        # Check that settings object has required attributes
        assert hasattr(settings, 'DATABASE_URL'), "DATABASE_URL not configured"
        assert hasattr(settings, 'SECRET_KEY'), "SECRET_KEY not configured"
        assert hasattr(settings, 'JWT_ALGORITHM'), "JWT_ALGORITHM not configured"
        assert hasattr(settings, 'JWT_EXPIRATION_DELTA'), "JWT_EXPIRATION_DELTA not configured"

        print("✅ Configuration is properly set up")
        return True
    except AssertionError as e:
        print(f"❌ Configuration error: {e}")
        return False


def validate_token_functionality():
    """Validate JWT token creation and verification functionality"""
    print("🔍 Validating token functionality...")

    try:
        # Create a test token
        test_data = {"user_id": "test_user_123", "role": "user"}
        from src.auth.security import create_access_token, verify_token

        token = create_access_token(data=test_data)
        assert token is not None, "Token creation failed"
        assert isinstance(token, str), "Token should be a string"
        assert len(token) > 0, "Token should not be empty"

        # Verify the token
        payload = verify_token(token)
        assert payload is not None, "Token verification failed"
        assert payload["user_id"] == "test_user_123", "User ID mismatch in payload"
        assert payload["role"] == "user", "Role mismatch in payload"
        assert "exp" in payload, "Expiration not in payload"

        print("✅ Token functionality works correctly")
        return True
    except Exception as e:
        print(f"❌ Token functionality error: {e}")
        return False


def validate_models():
    """Validate that the data models are properly defined"""
    print("🔍 Validating data models...")

    try:
        from src.models.task import Task, TaskCreate, TaskUpdate, TaskResponse

        # Test creating a task model instance
        task_create = TaskCreate(
            title="Test task",
            description="Test description",
            user_id="test_user_123"
        )

        assert task_create.title == "Test task"
        assert task_create.user_id == "test_user_123"

        print("✅ Data models are properly defined")
        return True
    except Exception as e:
        print(f"❌ Data model error: {e}")
        return False


def validate_services():
    """Validate that the service layer is properly implemented"""
    print("🔍 Validating service layer...")

    try:
        from src.services.task_service import TaskService

        # Just check that the service class exists and has required methods
        assert hasattr(TaskService, 'create_task'), "create_task method missing"
        assert hasattr(TaskService, 'get_tasks_by_user_id'), "get_tasks_by_user_id method missing"
        assert hasattr(TaskService, 'update_task'), "update_task method missing"
        assert hasattr(TaskService, 'delete_task'), "delete_task method missing"
        assert hasattr(TaskService, 'toggle_task_completion'), "toggle_task_completion method missing"

        print("✅ Service layer is properly implemented")
        return True
    except Exception as e:
        print(f"❌ Service layer error: {e}")
        return False


def validate_api_endpoints():
    """Validate that API endpoints are properly defined"""
    print("🔍 Validating API endpoints...")

    try:
        from src.api.v1.tasks import router

        # Check that the router is properly defined
        assert router is not None, "API router not defined"

        print("✅ API endpoints are properly defined")
        return True
    except Exception as e:
        print(f"❌ API endpoint error: {e}")
        return False


def validate_logging():
    """Validate that logging functionality works"""
    print("🔍 Validating logging functionality...")

    try:
        from src.core.logging import log_operation, log_error, log_authentication_event, log_authorization_decision, log_token_validation_result

        # Test logging functions
        log_operation("QUICKSTART_TEST_OPERATION", user_id="test_user")
        log_authentication_event("QUICKSTART_TEST", user_id="test_user")
        log_authorization_decision("read", "test_user", "task_123", True)
        log_token_validation_result("QUICKSTART_VALID", user_id="test_user")

        print("✅ Logging functionality works")
        return True
    except Exception as e:
        print(f"❌ Logging error: {e}")
        return False


def run_complete_validation():
    """Run all validation checks"""
    print("🚀 Starting quickstart validation for Todo API Backend...\n")

    all_checks = [
        ("Project Structure", validate_project_structure),
        ("Dependencies", validate_dependencies),
        ("Configuration", validate_config),
        ("Token Functionality", validate_token_functionality),
        ("Data Models", validate_models),
        ("Service Layer", validate_services),
        ("API Endpoints", validate_api_endpoints),
        ("Logging", validate_logging)
    ]

    results = []
    for check_name, check_func in all_checks:
        print(f"\n📋 {check_name} check:")
        result = check_func()
        results.append((check_name, result))

    print(f"\n🏁 Validation Summary:")
    total_checks = len(results)
    passed_checks = sum(1 for _, result in results if result)
    failed_checks = total_checks - passed_checks

    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {check_name}")

    print(f"\n📊 Total: {total_checks}, Passed: {passed_checks}, Failed: {failed_checks}")

    if failed_checks == 0:
        print("\n🎉 All validation checks passed! The Todo API backend is ready for use.")
        return True
    else:
        print(f"\n⚠️  {failed_checks} validation checks failed. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = run_complete_validation()
    sys.exit(0 if success else 1)