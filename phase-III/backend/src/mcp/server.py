"""
MCP Server Setup
"""

from typing import Dict, Any, List
from mcp import Server, tools
from .tools import add_task, list_tasks, complete_task, delete_task, update_task

async def create_mcp_server() -> Server:
    """
    Create and configure the MCP server with all task management tools
    """
    # Initialize MCP server
    server = Server()

    # Register all MCP tools
    server.tools.register(add_task)
    server.tools.register(list_tasks)
    server.tools.register(complete_task)
    server.tools.register(delete_task)
    server.tools.register(update_task)

    return server

async def register_mcp_tools(server: Server):
    """
    Register all MCP tools with an existing server instance
    """
    server.tools.register(add_task)
    server.tools.register(list_tasks)
    server.tools.register(complete_task)
    server.tools.register(delete_task)
    server.tools.register(update_task)

async def get_tool_descriptions() -> List[Dict[str, Any]]:
    """
    Get descriptions of all available MCP tools
    """
    return [
        {
            "name": "add_task",
            "description": "Create a new task with title and optional description",
            "input_schema": "AddTaskInput",
            "output_schema": "AddTaskOutput"
        },
        {
            "name": "list_tasks",
            "description": "List tasks with optional filters (completed, limit, offset)",
            "input_schema": "ListTasksInput",
            "output_schema": "ListTasksOutput"
        },
        {
            "name": "complete_task",
            "description": "Mark a task as complete by task ID",
            "input_schema": "CompleteTaskInput",
            "output_schema": "CompleteTaskOutput"
        },
        {
            "name": "delete_task",
            "description": "Delete a task by task ID",
            "input_schema": "DeleteTaskInput",
            "output_schema": "DeleteTaskOutput"
        },
        {
            "name": "update_task",
            "description": "Update task fields (title, description, completed)",
            "input_schema": "UpdateTaskInput",
            "output_schema": "UpdateTaskOutput"
        }
    ]