"""
OpenAI Agent Setup for Chat and Task Management
"""

import os
import json
from typing import Dict, Any, List, Optional
from openai import OpenAI

class ChatAgent:
    def __init__(self):
        """
        Initialize the OpenAI agent with system prompt and MCP tools
        """
        self.client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))

        # System prompt for task management
        self.system_prompt = self._create_system_prompt()

        # Register MCP tools
        self.tools = self._register_mcp_tools()

    def _create_system_prompt(self) -> str:
        """
        Create the system prompt for task management
        """
        return """You are a helpful AI assistant that helps users manage their tasks through natural conversation.

Your primary responsibilities:
1. Understand user requests and translate them into task management actions
2. Use the available tools to create, list, complete, delete, and update tasks
3. Maintain context from conversation history to understand references like "it", "that task", etc.
4. Respond in a helpful, conversational manner that confirms actions taken

Guidelines:
- Always confirm actions with the user (e.g., "Task created: Buy groceries")
- If a request is unclear, ask for clarification rather than guessing
- Use natural language and be friendly but professional
- Remember task context from previous messages
- Handle errors gracefully and suggest alternatives
- Don't make assumptions about user intent

Available Tools:
- add_task: Create new tasks with title and optional description
- list_tasks: List tasks with filters (completed status, limit, offset)
- complete_task: Mark tasks as complete by ID
- delete_task: Delete tasks by ID
- update_task: Update task fields (title, description, completed status)

Always use these tools to interact with the task system rather than making assumptions."""

    def _register_mcp_tools(self) -> List[Dict[str, Any]]:
        """
        Register MCP tools as OpenAI function calling tools
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Create a new task with title and optional description",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The title of the task"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional description of the task"
                            }
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "List tasks with optional filters (completed, limit, offset)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "completed": {
                                "type": "boolean",
                                "description": "Filter by completion status"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of tasks to return"
                            },
                            "offset": {
                                "type": "integer",
                                "description": "Number of tasks to skip"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Mark a task as complete by task ID",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID of the task to complete"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Delete a task by task ID",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID of the task to delete"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update task fields (title, description, completed)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID of the task to update"
                            },
                            "title": {
                                "type": "string",
                                "description": "New title for the task"
                            },
                            "description": {
                                "type": "string",
                                "description": "New description for the task"
                            },
                            "completed": {
                                "type": "boolean",
                                "description": "New completion status"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            }
        ]

    async def process_message(self, message: str, context: List[Dict[str, Any]],
                            user_id: str) -> Dict[str, Any]:
        """
        Process a user message with conversation context

        Args:
            message: User's message text
            context: List of previous messages in conversation
            user_id: ID of the authenticated user

        Returns:
            Dictionary with AI response text and list of tool calls executed
        """
        # Build chat history
        chat_history = self._build_chat_history(context)

        # Create messages for OpenAI API
        messages = [
            {"role": "system", "content": self.system_prompt}
        ] + chat_history + [
            {"role": "user", "content": message}
        ]

        try:
            # Call OpenAI API (synchronous client for simplicity)
            response = self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4"),
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=0.7
            )

            # Extract response and tool calls
            ai_message = response.choices[0].message
            ai_response = ai_message.content
            tool_calls = []

            # Process any function calls
            if ai_message.tool_calls:
                for tool_call in ai_message.tool_calls:
                    tool_calls.append({
                        "id": tool_call.id,
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    })

            return {
                "ai_response": ai_response,
                "tool_calls": tool_calls
            }
        except Exception as e:
            # Return error response
            return {
                "ai_response": f"I apologize, but I encountered an error processing your request: {str(e)}",
                "tool_calls": [],
                "error": str(e)
            }

    def _build_chat_history(self, context: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Build chat history from database context

        Args:
            context: List of message dictionaries from database

        Returns:
            List of message dictionaries for OpenAI API
        """
        messages = []
        for msg in context:
            role = "user" if msg.get("sender") == "user" else "assistant"
            messages.append({"role": role, "content": msg.get("content", "")})

        return messages

    async def execute_tool_calls(self, tool_calls: List[Dict[str, Any]],
                               user_id: str, session) -> List[Dict[str, Any]]:
        """
        Execute MCP tool calls and return results

        Args:
            tool_calls: List of tool call dictionaries
            user_id: ID of the authenticated user
            session: Database session

        Returns:
            List of tool execution results
        """
        from src.services.task_service import TaskService

        results = []
        task_service = TaskService()

        for tool_call in tool_calls:
            tool_name = tool_call.get("name", "")
            arguments_str = tool_call.get("arguments", "{}")

            try:
                # Parse arguments
                args = json.loads(arguments_str) if arguments_str else {}

                # Execute the appropriate tool
                result = None
                if tool_name == "add_task":
                    result = task_service.create_task(
                        session=session,
                        user_id=user_id,
                        title=args.get("title"),
                        description=args.get("description")
                    )
                    result = {"id": result.id, "title": result.title, "description": result.description}

                elif tool_name == "list_tasks":
                    tasks = task_service.list_tasks(
                        session=session,
                        user_id=user_id,
                        completed=args.get("completed"),
                        limit=args.get("limit", 20),
                        offset=args.get("offset", 0)
                    )
                    result = [{"id": t.id, "title": t.title, "description": t.description, "completed": t.completed} for t in tasks]

                elif tool_name == "complete_task":
                    success = task_service.complete_task(
                        session=session,
                        task_id=args.get("task_id"),
                        user_id=user_id
                    )
                    result = {"success": success, "task_id": args.get("task_id")}

                elif tool_name == "delete_task":
                    success = task_service.delete_task(
                        session=session,
                        task_id=args.get("task_id"),
                        user_id=user_id
                    )
                    result = {"success": success, "task_id": args.get("task_id")}

                elif tool_name == "update_task":
                    task = task_service.update_task(
                        session=session,
                        task_id=args.get("task_id"),
                        user_id=user_id,
                        title=args.get("title"),
                        description=args.get("description"),
                        completed=args.get("completed")
                    )
                    if task:
                        result = {"id": task.id, "title": task.title, "description": task.description, "completed": task.completed}
                    else:
                        result = {"error": "Task not found or access denied"}

                results.append({
                    "tool": tool_name,
                    "success": True,
                    "result": result,
                    "arguments": args
                })

            except Exception as e:
                results.append({
                    "tool": tool_name,
                    "success": False,
                    "error": str(e),
                    "arguments": arguments_str
                })

        return results
