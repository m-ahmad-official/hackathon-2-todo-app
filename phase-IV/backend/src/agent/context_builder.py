"""
Context Builder for OpenAI Agent
"""

from typing import List, Dict, Any
from datetime import datetime

class ContextBuilder:
    def __init__(self, max_messages: int = 20, max_tokens: int = 8000):
        """
        Initialize context builder with limits

        Args:
            max_messages: Maximum number of messages to include in context
            max_tokens: Maximum token count for context
        """
        self.max_messages = max_messages
        self.max_tokens = max_tokens

    def build_context(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Build conversation context for OpenAI agent

        Args:
            messages: List of message dictionaries from database

        Returns:
            List of messages formatted for OpenAI API
        """
        # Get recent messages (newest first)
        recent_messages = self._get_recent_messages(messages)

        # Format messages for OpenAI
        formatted_messages = self._format_messages(recent_messages)

        return formatted_messages

    def _get_recent_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get recent messages with token counting

        Args:
            messages: List of all messages

        Returns:
            List of recent messages within token limits
        """
        # Sort messages by created_at (newest first)
        sorted_messages = sorted(messages, key=lambda x: x["created_at"], reverse=True)

        # Take up to max_messages
        recent_messages = sorted_messages[:self.max_messages]

        # Sort back to chronological order (oldest first)
        recent_messages = sorted(recent_messages, key=lambda x: x["created_at"])

        return recent_messages

    def _format_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format messages for OpenAI API

        Args:
            messages: List of message dictionaries

        Returns:
            List of formatted messages
        """
        formatted = []
        for msg in messages:
            formatted.append({
                "role": "user" if msg["sender"] == "user" else "assistant",
                "content": msg["content"]
            })

        return formatted

    def count_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """
        Count tokens in message list

        Args:
            messages: List of message dictionaries

        Returns:
            Token count
        """
        from tiktoken import encoding_for_model
        import math

        # Get GPT-4 tokenizer
        tokenizer = encoding_for_model("gpt-4")

        # Count tokens in all messages
        token_count = 0
        for msg in messages:
            content = msg.get("content", "")
            token_count += len(tokenizer.encode(content))

        return token_count

    def should_truncate(self, messages: List[Dict[str, Any]]) -> bool:
        """
        Check if messages should be truncated based on token limits

        Args:
            messages: List of message dictionaries

        Returns:
            True if truncation is needed
        """
        token_count = self.count_tokens(messages)
        return token_count > self.max_tokens

    def truncate_context(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Truncate context to fit within token limits

        Args:
            messages: List of message dictionaries

        Returns:
            Truncated list of messages
        """
        # Start with all messages
        current_messages = messages.copy()

        # Keep removing oldest messages until within token limit
        while current_messages and self.count_tokens(current_messages) > self.max_tokens:
            current_messages = current_messages[1:]  # Remove oldest message

        return current_messages

    def get_context_summary(self, messages: List[Dict[str, Any]]) -> str:
        """
        Create a summary of conversation context

        Args:
            messages: List of message dictionaries

        Returns:
            Summary string
        """
        if not messages:
            return "New conversation"

        # Get last few messages for summary
        recent = messages[-3:] if len(messages) > 3 else messages

        summary_parts = []
        for msg in recent:
            role = "User" if msg["sender"] == "user" else "AI"
            summary_parts.append(f"{role}: {msg['content'][:50]}{'...' if len(msg['content']) > 50 else ''}")

        return " | ".join(summary_parts)

    def validate_context(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate context for processing

        Args:
            messages: List of message dictionaries

        Returns:
            Validation result with warnings if any
        """
        validation = {"valid": True, "warnings": []}

        # Check message count
        if len(messages) > self.max_messages:
            validation["valid"] = False
            validation["warnings"].append(
                f"Message count {len(messages)} exceeds maximum {self.max_messages}"
            )

        # Check token count
        token_count = self.count_tokens(messages)
        if token_count > self.max_tokens:
            validation["valid"] = False
            validation["warnings"].append(
                f"Token count {token_count} exceeds maximum {self.max_tokens}"
            )

        return validation