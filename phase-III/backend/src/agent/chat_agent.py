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
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("WARNING: OPENAI_API_KEY not set. Using mock/demo mode for AI chat.")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)

        # System prompt for task management
        self.system_prompt = self._create_system_prompt()

        # Register MCP tools
        self.tools = self._register_mcp_tools()

    def _process_message_mock(self, message: str, context: List[Dict[str, Any]],
                            user_id: str) -> Dict[str, Any]:
        """
        Process a message in mock/demo mode without OpenAI API
        This provides basic functionality for testing when API key is not available
        """
        message_lower = message.lower().strip()

        # Simple rule-based responses
        tool_calls = []
        ai_response = ""

        # Check for task creation intent
        if any(phrase in message_lower for phrase in ["create", "add", "new", "make"]):
            if "task" in message_lower or "todo" in message_lower or "item" in message_lower:
                # Extract task title (simple extraction - take words after "task" or similar)
                words = message.split()
                title_idx = -1
                for i, word in enumerate(words):
                    if word.lower() in ["task", "todo", "item"]:
                        title_idx = i + 1
                        break

                if title_idx >= 0 and title_idx < len(words):
                    title = " ".join(words[title_idx:])
                    # Remove common stop words
                    title = title.replace(" called ", " ").replace(" named ", " ").replace(" to ", " ").strip()
                    if title:
                        tool_calls.append({
                            "id": "mock-call-1",
                            "name": "add_task",
                            "arguments": json.dumps({"title": title})
                        })
                        ai_response = f"I'll create a task: '{title}'"
                    else:
                        ai_response = "What would you like to name the task?"
                else:
                    ai_response = "I can help you create a task. What should it be called?"

        # Check for listing tasks
        elif any(phrase in message_lower for phrase in ["list", "show", "get", "what", "view"]):
            if "task" in message_lower:
                tool_calls.append({
                    "id": "mock-call-2",
                    "name": "list_tasks",
                    "arguments": json.dumps({})
                })
                ai_response = "I'll retrieve your tasks for you."

        # Check for completing tasks
        elif any(phrase in message_lower for phrase in ["complete", "done", "finished", "mark", "incomplete", "not done", "unfinished"]):
            if "task" in message_lower:
                # Check if user specified a task number
                words = message.split()
                task_id = None
                for word in words:
                    if word.isdigit():
                        task_id = int(word)
                        break

                if task_id:
                    # Directly complete the specified task
                    tool_calls.append({
                        "id": "mock-call-3",
                        "name": "complete_task",
                        "arguments": json.dumps({"task_id": task_id})
                    })
                    ai_response = f"I'll mark task {task_id} as complete."
                else:
                    # Need to list tasks first
                    tool_calls.append({
                        "id": "mock-call-3",
                        "name": "list_tasks",
                        "arguments": json.dumps({})
                    })
                    ai_response = "I'll help you mark a task as complete. Let me first show you your tasks."

        # Check for deleting tasks
        elif any(phrase in message_lower for phrase in ["delete", "remove", "cancel"]):
            if "task" in message_lower:
                # Check if user specified a task number
                words = message.split()
                task_id = None
                for word in words:
                    if word.isdigit():
                        task_id = int(word)
                        break

                if task_id:
                    # Directly delete the specified task
                    tool_calls.append({
                        "id": "mock-call-4",
                        "name": "delete_task",
                        "arguments": json.dumps({"task_id": task_id})
                    })
                    ai_response = f"I'll delete task {task_id}."
                else:
                    # Need to list tasks first
                    tool_calls.append({
                        "id": "mock-call-4",
                        "name": "list_tasks",
                        "arguments": json.dumps({})
                    })
                    ai_response = "I'll help you delete a task. Let me first show you your tasks."

        # Default response
        else:
            ai_response = "I'm here to help you manage your tasks. You can ask me to create, list, complete, or delete tasks. What would you like to do?"

        return {
            "ai_response": ai_response,
            "tool_calls": tool_calls
        }

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
            # Check if OpenAI client is available
            if not self.client:
                # Use mock/demo mode when no API key is configured
                return self._process_message_mock(message, context, user_id)

            # Call OpenAI API (synchronous client for simplicity)
            response = self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=0.7
            )

            # Extract response and tool calls
            ai_message = response.choices[0].message
            ai_response = ai_message.content
            tool_calls = []

            # Process any function calls first
            if ai_message.tool_calls:
                for tool_call in ai_message.tool_calls:
                    tool_calls.append({
                        "id": tool_call.id,
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    })

            # If AI response is None (e.g., when only tool calls are made), generate a default response
            if ai_response is None:
                if tool_calls:
                    # Build a response based on tool calls made
                    tool_names = [tc.get("name") for tc in tool_calls]
                    ai_response = f"I've processed your request using the following tools: {', '.join(tool_names)}."
                else:
                    ai_response = "I processed your request."

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
        from src.models.task import TaskCreate

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
                    # Create TaskCreate object with user_id
                    task_create = TaskCreate(
                        user_id=user_id,
                        title=args.get("title"),
                        description=args.get("description")
                    )
                    db_task = task_service.create_task(
                        session=session,
                        task_create=task_create
                    )
                    result = {"id": db_task.id, "title": db_task.title, "description": db_task.description}

                elif tool_name == "list_tasks":
                    # Use get_tasks_by_user_id instead of list_tasks
                    tasks = task_service.get_tasks_by_user_id(
                        session=session,
                        user_id=user_id
                    )
                    result = [{"id": t.id, "title": t.title, "description": t.description, "completed": t.completed} for t in tasks]

                elif tool_name == "complete_task":
                    # Use toggle_task_completion instead of complete_task
                    task = task_service.toggle_task_completion(
                        session=session,
                        task_id=args.get("task_id"),
                        current_user_id=user_id
                    )
                    if task:
                        result = {"success": True, "task_id": args.get("task_id"), "completed": task.completed}
                    else:
                        result = {"success": False, "task_id": args.get("task_id")}

                elif tool_name == "delete_task":
                    success = task_service.delete_task(
                        session=session,
                        task_id=args.get("task_id"),
                        current_user_id=user_id
                    )
                    result = {"success": success, "task_id": args.get("task_id")}

                elif tool_name == "update_task":
                    task = task_service.update_task(
                        session=session,
                        task_id=args.get("task_id"),
                        current_user_id=user_id,
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
