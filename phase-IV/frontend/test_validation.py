#!/usr/bin/env python3
"""
Validation script to check that all required components are in place for the backend
"""
import os
import sys
from pathlib import Path

def validate_backend_structure():
    """Validate that all required backend files exist and have correct structure"""
    print("🔍 Validating backend structure...")

    required_paths = [
        # Core structure
        "backend/src/main.py",
        "backend/src/models/task.py",
        "backend/src/services/task_service.py",
        "backend/src/api/v1/tasks.py",
        "backend/src/auth/security.py",
        "backend/src/auth/deps.py",
        "backend/src/core/config.py",
        "backend/src/core/database.py",
        "backend/src/core/logging.py",

        # Dependencies
        "backend/requirements.txt",
        "backend/.env.example",

        # Documentation
        "backend/docs/api-reference.md",

        # Tests
        "backend/tests/unit/test_models/test_task.py",
        "backend/tests/integration/test_auth_flow.py"
    ]

    missing_paths = []
    for path in required_paths:
        full_path = Path(path)
        if not full_path.exists():
            missing_paths.append(str(full_path))

    if missing_paths:
        print(f"❌ Missing backend files: {missing_paths}")
        return False

    print("✅ All required backend files exist")
    return True


def validate_frontend_structure():
    """Validate that all required frontend files exist and have correct structure"""
    print("🔍 Validating frontend structure...")

    required_paths = [
        # Core structure
        "frontend/src/models/task.ts",
        "frontend/src/services/task-service.ts",
        "frontend/src/services/api-client.ts",
        "frontend/src/services/auth-service.ts",
        "frontend/src/components/auth/SignInForm.tsx",
        "frontend/src/components/auth/SignUpForm.tsx",
        "frontend/src/components/tasks/TaskItem.tsx",
        "frontend/src/components/tasks/TaskList.tsx",
        "frontend/src/components/tasks/TaskForm.tsx",
        "frontend/src/providers/AuthProvider.tsx",
        "frontend/src/lib/logging.ts",
        "frontend/src/lib/error-handler.ts",

        # Pages
        "frontend/src/app/(auth)/sign-in/page.tsx",
        "frontend/src/app/(auth)/sign-up/page.tsx",
        "frontend/src/app/dashboard/page.tsx",
        "frontend/src/app/dashboard/layout.tsx",

        # Configuration
        "frontend/package.json",
        "frontend/.env.example",

        # Documentation
        "frontend/docs/api-reference.md",

        # Tests
        "frontend/tests/unit/test_auth/test_auth_functions.py",
        "frontend/tests/integration/test_expired_tokens.py"
    ]

    missing_paths = []
    for path in required_paths:
        full_path = Path(path)
        if not full_path.exists():
            missing_paths.append(str(full_path))

    if missing_paths:
        print(f"❌ Missing frontend files: {missing_paths}")
        return False

    print("✅ All required frontend files exist")
    return True


def validate_env_vars():
    """Validate that required environment variables are configured"""
    print("🔍 Validating environment configuration...")

    # Check that .env.example exists and has required variables
    env_example_path = Path("backend") / ".env.example"
    if not env_example_path.exists():
        print("❌ backend/.env.example file not found")
        return False

    with open(env_example_path, 'r') as f:
        env_content = f.read()

    required_vars = [
        "DATABASE_URL",
        "SECRET_KEY",
        "BETTER_AUTH_SECRET",
        "BETTER_AUTH_PUBLIC_KEY",
        "JWT_ALGORITHM",
        "JWT_EXPIRATION_DELTA"
    ]

    missing_vars = []
    for var in required_vars:
        if var not in env_content:
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Missing environment variables in .env.example: {missing_vars}")
        return False

    print("✅ Environment variables properly configured")
    return True


def validate_dependencies():
    """Validate that required dependencies are in requirements.txt"""
    print("🔍 Validating dependencies...")

    requirements_path = Path("backend") / "requirements.txt"
    if not requirements_path.exists():
        print("❌ backend/requirements.txt file not found")
        return False

    with open(requirements_path, 'r') as f:
        req_content = f.read()

    required_deps = [
        "fastapi",
        "sqlmodel",
        "pydantic",
        "jose",
        "python-jose",
        "cryptography",
        "uvicorn",
        "asyncpg",
        "psycopg2-binary",
        "alembic",
        "pytest",
        "httpx"
    ]

    missing_deps = []
    for dep in required_deps:
        if dep not in req_content.lower():  # Case insensitive search
            missing_deps.append(dep)

    if missing_deps:
        print(f"❌ Missing dependencies in requirements.txt: {missing_deps}")
        return False

    print("✅ Dependencies properly configured")
    return True


def validate_frontend_dependencies():
    """Validate that required frontend dependencies are in package.json"""
    print("🔍 Validating frontend dependencies...")

    package_json_path = Path("frontend") / "package.json"
    if not package_json_path.exists():
        print("❌ frontend/package.json file not found")
        return False

    import json
    with open(package_json_path, 'r') as f:
        package_json = json.load(f)

    required_deps = [
        "next",
        "react",
        "react-dom",
        "better-auth",
        "react-hook-form",
        "swr",
        "@hookform/resolvers",
        "zod",
        "axios"
    ]

    all_deps = {**package_json.get('dependencies', {}), **package_json.get('devDependencies', {})}

    missing_deps = []
    for dep in required_deps:
        if not any(req_dep in all_deps for req_dep in [dep]):
            missing_deps.append(dep)

    if missing_deps:
        print(f"❌ Missing frontend dependencies in package.json: {missing_deps}")
        return False

    print("✅ Frontend dependencies properly configured")
    return True


def run_complete_validation():
    """Run all validation checks"""
    print("🚀 Starting complete validation for Todo API Backend & Frontend...\n")

    checks = [
        ("Backend Structure", validate_backend_structure),
        ("Frontend Structure", validate_frontend_structure),
        ("Environment Variables", validate_env_vars),
        ("Backend Dependencies", validate_dependencies),
        ("Frontend Dependencies", validate_frontend_dependencies)
    ]

    results = []
    for check_name, check_func in checks:
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
        print("\n🎉 All validation checks passed! The Todo API backend and frontend are ready for use.")
        return True
    else:
        print(f"\n⚠️  {failed_checks} validation checks failed. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = run_complete_validation()
    sys.exit(0 if success else 1)