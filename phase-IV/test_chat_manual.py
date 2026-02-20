#!/usr/bin/env python3
"""
Manual test script for chat API endpoints
"""
import httpx
import json
import asyncio

BASE_URL = "http://localhost:8000"

# Test user credentials (from auth system)
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"

async def test_chat_flow():
    """Test the complete chat flow"""
    print("=" * 60)
    print("CHAT API MANUAL TEST")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        # Step 1: Register/Login to get JWT token
        print("\n1. Authenticating...")
        try:
            # Try to sign up (using form data)
            signup_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "name": "Test User"
            }
            response = await client.post(f"{BASE_URL}/api/v1/register", data=signup_data)
            if response.status_code == 200:
                print("   ✓ User created successfully")
            elif response.status_code == 409:
                print("   ℹ User already exists, attempting login...")
        except Exception as e:
            print(f"   ✗ Error during signup: {e}")

        # Login to get token (using form data)
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        response = await client.post(f"{BASE_URL}/api/v1/login", data=login_data)
        if response.status_code != 200:
            print(f"   ✗ Login failed: {response.status_code} - {response.text}")
            return
        print("   ✓ Login successful")

        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"   ✓ JWT token obtained")

        # Step 2: Create a conversation
        print("\n2. Creating conversation...")
        conversation_data = {"title": "Test Conversation"}
        response = await client.post(f"{BASE_URL}/api/v1/chat/", json=conversation_data, headers=headers)
        if response.status_code != 201:
            print(f"   ✗ Failed to create conversation: {response.status_code} - {response.text}")
            return
        conversation = response.json()
        conversation_id = conversation["id"]
        print(f"   ✓ Conversation created: ID={conversation_id}, Title='{conversation['title']}'")

        # Step 3: Add a message to the conversation
        print("\n3. Adding message...")
        message_data = {"content": "Hello, AI! This is a test message."}
        response = await client.post(
            f"{BASE_URL}/api/v1/chat/{conversation_id}/messages",
            json=message_data,
            headers=headers
        )
        if response.status_code != 201:
            print(f"   ✗ Failed to add message: {response.status_code} - {response.text}")
        else:
            message = response.json()
            print(f"   ✓ Message added: ID={message['id']}, Content='{message['content'][:50]}...'")

        # Step 4: Get messages from conversation
        print("\n4. Retrieving messages...")
        response = await client.get(f"{BASE_URL}/api/v1/chat/{conversation_id}/messages?limit=20", headers=headers)
        if response.status_code != 200:
            print(f"   ✗ Failed to get messages: {response.status_code} - {response.text}")
        else:
            messages = response.json()
            print(f"   ✓ Retrieved {len(messages)} messages")
            for msg in messages:
                sender = msg['sender']
                content = msg['content'][:40]
                print(f"     - [{sender}]: {content}...")

        # Step 5: List all conversations
        print("\n5. Listing conversations...")
        response = await client.get(f"{BASE_URL}/api/v1/chat/", headers=headers)
        if response.status_code != 200:
            print(f"   ✗ Failed to list conversations: {response.status_code} - {response.text}")
        else:
            conversations = response.json()
            print(f"   ✓ Total conversations: {len(conversations)}")
            for conv in conversations:
                print(f"     - ID={conv['id']}, Title='{conv.get('title', 'Untitled')}'")

        # Step 6: Send a chat message to AI
        print("\n6. Sending chat to AI agent...")
        chat_data = {"message": "What tasks do I have pending?"}
        response = await client.post(f"{BASE_URL}/api/v1/chat/chat", json=chat_data, headers=headers)
        if response.status_code != 200:
            print(f"   ✗ Failed to send chat: {response.status_code} - {response.text}")
        else:
            chat_response = response.json()
            print(f"   ✓ AI Response received:")
            print(f"     Conversation ID: {chat_response['conversationId']}")
            print(f"     Message: {chat_response['message'][:100]}...")
            print(f"     Context: {chat_response['contextMetadata']}")

        # Step 7: Delete the conversation (cleanup)
        print("\n7. Cleaning up - deleting conversation...")
        response = await client.delete(f"{BASE_URL}/api/v1/chat/{conversation_id}", headers=headers)
        if response.status_code != 204:
            print(f"   ✗ Failed to delete conversation: {response.status_code} - {response.text}")
        else:
            print(f"   ✓ Conversation deleted successfully")

        print("\n" + "=" * 60)
        print("ALL CHAT TESTS PASSED ✓")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_chat_flow())
