"""
Unit tests for MCP Tools
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from backend.src.mcp.tools import add_task, list_tasks, complete_task, delete_task, update_task

class TestMCPTools:
    @pytest.fixture
    def mock_context(self):
        return {"user_id": "test_user_123"}

    @pytest.fixture
    def mock_invalid_context(self):
        return {}

    @pytest.fixture
    def mock_task_service(self):
        return AsyncMock()

    @pytest.fixture
    def mock_get_session(self):
        async def mock_session():
            return AsyncMock()
        return mock_session

    @pytest.mark.asyncio
    @pytest.mark.parametrize("input_data", [
        {"title": "Buy groceries", "description": "Milk, eggs, bread"},
        {"title": "Call mom", "priority": "high"},
        {"title": "Finish project"}
    ])
    async def test_add_task_success(self, input_data, mock_context):
        """Test add_task with valid input"""
        # Mock the task service
        with patch("backend.src.services.task_service.TaskService.create_task", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = AsyncMock(id=1)

            result = await add_task(input_data, mock_context)

            assert result.success is True
            assert result.task_id == 1
            mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_task_invalid_context(self, input_data):
        """Test add_task with missing user_id"""
        result = await add_task(input_data, {})
        assert result.success is False
        assert "User ID not found" in result.error

    @pytest.mark.asyncio
    @pytest.mark.parametrize("input_data, expected_error", [
        ({}, "title"),
        ({ "title": "" }, "min_length"),
        ({ "title": "a" * 256 }, "max_length")
    ])
    async def test_add_task_validation_errors(self, input_data, expected_error):
        """Test add_task validation errors"""
        result = await add_task(input_data, {"user_id": "test_user"})
        assert result.success is False
        assert "error" in result.error.lower()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("input_data", [
        {"completed": True, "limit": 10, "offset": 0},
        {"completed": False, "limit": 5},
        {"limit": 20}
    ])
    async def test_list_tasks_success(self, input_data, mock_context):
        """Test list_tasks with valid input"""
        # Mock the task service
        with patch("backend.src.services.task_service.TaskService.list_tasks", new_callable=AsyncMock) as mock_list,
             patch("backend.src.services.task_service.TaskService.count_tasks", new_callable=AsyncMock) as mock_count:
            mock_list.return_value = [AsyncMock(id=1, title="Task 1")]
            mock_count.return_value = 1

            result = await list_tasks(input_data, mock_context)

            assert result.success is True
            assert len(result.tasks) == 1
            assert result.total == 1
            mock_list.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_tasks_invalid_context(self):
        """Test list_tasks with missing user_id"""
        result = await list_tasks({"limit": 10}, {})
        assert result.success is False
        assert "User ID not found" in result.error

    @pytest.mark.asyncio
    async def test_complete_task_success(self, mock_context):
        """Test complete_task with valid input"""
        # Mock the task service
        with patch("backend.src.services.task_service.TaskService.update_task", new_callable=AsyncMock) as mock_update:
            mock_update.return_value = AsyncMock(id=1, completed=True)

            result = await complete_task({"task_id": 1}, mock_context)

            assert result.success is True
            assert result.task_completed is True
            mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_complete_task_invalid_context(self):
        """Test complete_task with missing user_id"""
        result = await complete_task({"task_id": 1}, {})
        assert result.success is False
        assert "User ID not found" in result.error

    @pytest.mark.asyncio
    async def test_delete_task_success(self, mock_context):
        """Test delete_task with valid input"""
        # Mock the task service
        with patch("backend.src.services.task_service.TaskService.delete_task", new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = True

            result = await delete_task({"task_id": 1}, mock_context)

            assert result.success is True
            assert result.task_deleted is True
            mock_delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_task_invalid_context(self):
        """Test delete_task with missing user_id"""
        result = await delete_task({"task_id": 1}, {})
        assert result.success is False
        assert "User ID not found" in result.error

    @pytest.mark.asyncio
    @pytest.mark.parametrize("input_data", [
        {"task_id": 1, "title": "Updated title"},
        {"task_id": 1, "description": "New description"},
        {"task_id": 1, "completed": True},
        {"task_id": 1, "title": "New title", "completed": False}
    ])
    async def test_update_task_success(self, input_data, mock_context):
        """Test update_task with valid input"""
        # Mock the task service
        with patch("backend.src.services.task_service.TaskService.update_task", new_callable=AsyncMock) as mock_update:
            mock_update.return_value = AsyncMock(id=1, title="Updated title")

            result = await update_task(input_data, mock_context)

            assert result.success is True
            assert result.task is not None
            mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_task_invalid_context(self):
        """Test update_task with missing user_id"""
        result = await update_task({"task_id": 1}, {})
        assert result.success is False
        assert "User ID not found" in result.error

    @pytest.mark.asyncio
    async def test_user_id_enforcement(self, mock_context):
        """Test that all tools enforce user_id"""
        invalid_context = {}

        # Test each tool with invalid context
        result_add = await add_task({"title": "Test"}, invalid_context)
        result_list = await list_tasks({"limit": 10}, invalid_context)
        result_complete = await complete_task({"task_id": 1}, invalid_context)
        result_delete = await delete_task({"task_id": 1}, invalid_context)
        result_update = await update_task({"task_id": 1}, invalid_context)

        # All should fail with user_id error
        assert result_add.success is False
        assert result_list.success is False
        assert result_complete.success is False
        assert result_delete.success is False
        assert result_update.success is False

        assert "User ID not found" in result_add.error.lower()
        assert "User ID not found" in result_list.error.lower()
        assert "User ID not found" in result_complete.error.lower()
        assert "User ID not found" in result_delete.error.lower()
        assert "User ID not found" in result_update.error.lower()