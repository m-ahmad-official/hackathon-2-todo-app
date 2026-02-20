# Chat API Client Documentation

This documentation covers the frontend chat API client for the AI chat backend.

## Overview

The chat API client provides a type-safe, production-ready interface for interacting with the AI chat backend. It handles authentication, error handling, and provides a consistent API for chat-related operations.

## Installation and Setup

### Dependencies
The chat API client uses the following dependencies:
- `axios` for HTTP requests
- Custom logging utilities
- TypeScript for type safety

### Environment Variables
Ensure the following environment variables are set:
```typescript
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

## API Models and Types

### Core Types

#### Message
```typescript
interface Message {
  id: number;
  conversationId: number;
  content: string;
  sender: "user" | "ai";
  createdAt: string;
  metadata?: Record<string, any>;
}
```

#### Conversation
```typescript
interface Conversation {
  id: number;
  userId: string;
  title?: string;
  createdAt: string;
  updatedAt: string;
  messageCount: number;
  lastMessage?: string;
}
```

### Request Types

#### CreateConversationRequest
```typescript
interface CreateConversationRequest {
  title?: string;
}
```

#### GetConversationRequest
```typescript
interface GetConversationRequest {
  conversationId: number;
}
```

#### ListConversationsRequest
```typescript
interface ListConversationsRequest {
  limit?: number;
  offset?: number;
}
```

#### DeleteConversationRequest
```typescript
interface DeleteConversationRequest {
  conversationId: number;
}
```

#### AddMessageRequest
```typescript
interface AddMessageRequest {
  conversationId: number;
  content: string;
  metadata?: Record<string, any>;
}
```

### Response Types

#### ApiResponse<T>
```typescript
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ChatApiError;
  timestamp: string;
}
```

#### ChatApiError
```typescript
interface ChatApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
}
```

## API Methods

### createChatConversation(request)

Creates a new chat conversation for the authenticated user.

**Parameters:**
- `request`: CreateConversationRequest

**Returns:** Promise<ApiResponse<Conversation>>

**Example:**
```typescript
const response = await chatApiService.createChatConversation({
  title: "My AI Conversation",
});

if (response.success) {
  console.log(`Created conversation: ${response.data.id}`);
}
```

### getConversation(request)

Retrieves a specific conversation by ID.

**Parameters:**
- `request`: GetConversationRequest

**Returns:** Promise<ApiResponse<Conversation>>

**Example:**
```typescript
const response = await chatApiService.getConversation({
  conversationId: 123,
});

if (response.success) {
  console.log(`Conversation title: ${response.data.title}`);
}
```

### listConversations(request?)

Lists all conversations for the authenticated user with pagination.

**Parameters:**
- `request?`: ListConversationsRequest (optional)

**Returns:** Promise<ApiResponse<Conversation[]>>

**Example:**
```typescript
const response = await chatApiService.listConversations({
  limit: 20,
  offset: 0,
});

if (response.success) {
  console.log(`Found ${response.data.length} conversations`);
}
```

### deleteConversation(request)

Deletes a conversation by ID.

**Parameters:**
- `request`: DeleteConversationRequest

**Returns:** Promise<ApiResponse<void>>

**Example:**
```typescript
const response = await chatApiService.deleteConversation({
  conversationId: 123,
});

if (response.success) {
  console.log("Conversation deleted successfully");
}
```

### addMessage(request)

Adds a message to a conversation.

**Parameters:**
- `request`: AddMessageRequest

**Returns:** Promise<ApiResponse<Message>>

**Example:**
```typescript
const response = await chatApiService.addMessage({
  conversationId: 123,
  content: "Hello, I need help with my project",
});

if (response.success) {
  console.log(`Message added: ${response.data.id}`);
}
```

### getMessages(conversationId, limit?)

Retrieves messages from a conversation.

**Parameters:**
- `conversationId`: number
- `limit?`: number (optional, default 20)

**Returns:** Promise<ApiResponse<Message[]>>

**Example:**
```typescript
const response = await chatApiService.getMessages(123, 50);

if (response.success) {
  console.log(`Found ${response.data.length} messages`);
}
```

## Error Handling

The chat API client provides comprehensive error handling with the following methods:

### isAuthenticationError(error)
Checks if an error is an authentication-related error.

**Returns:** boolean

### isValidationError(error)
Checks if an error is a validation-related error.

**Returns:** boolean

### isNotFoundError(error)
Checks if an error is a not-found-related error.

**Returns:** boolean

## Authentication

The API client automatically handles JWT authentication:

1. **Token Attachment**: JWT tokens are automatically attached to requests via interceptors
2. **401 Handling**: Automatically redirects to login page on 401 responses
3. **Token Storage**: Uses localStorage for token persistence

## Logging

All API operations are automatically logged using the logging utility:
- Operation start and success
- Error conditions
- Authentication events

## Usage Examples

### Basic Chat Flow

```typescript
import { chatApiService } from "./api/chat-api";
import { chatApiExamples } from "./api/chat-api-examples";

// Create a conversation
const conversation = await chatApiService.createChatConversation({
  title: "My AI Chat",
});

// Add messages
await chatApiService.addMessage({
  conversationId: conversation.data.id,
  content: "Hello, how are you?",
});

// Get conversation messages
const messages = await chatApiService.getMessages(conversation.data.id);

// List all conversations
const conversations = await chatApiService.listConversations();
```

### Using Examples

```typescript
// Import examples
import { chatApiExamples } from "./api/chat-api-examples";

// Run complete chat workflow example
await chatApiExamples.exampleCompleteChatWorkflow();

// Create conversation example
await chatApiExamples.exampleCreateConversation();

// List conversations example
await chatApiExamples.exampleListConversations();
```

## Testing

The chat API client includes comprehensive unit tests:

```bash
npm test src/api/__tests__/chat-api.test.ts
```

## Best Practices

1. **Error Handling**: Always check the `success` property in API responses
2. **Authentication**: Handle authentication errors gracefully
3. **Pagination**: Use pagination for listing operations
4. **Type Safety**: Leverage TypeScript types for request/response validation
5. **Logging**: Use provided logging for debugging and monitoring

## Integration

The chat API client integrates seamlessly with the existing frontend architecture:

- Uses the shared `apiClient` for HTTP requests
- Integrates with authentication services
- Follows the existing logging patterns
- Compatible with the existing error handling utilities

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Ensure JWT token is properly set in localStorage
2. **Network Errors**: Check API_BASE_URL and network connectivity
3. **Type Errors**: Verify request data matches TypeScript interfaces
4. **CORS Issues**: Ensure proper CORS configuration on the backend

### Debug Logging

Enable debug logging by checking the browser console for log_operation calls.

## Future Enhancements

- WebSocket support for real-time messaging
- Message streaming for large conversations
- Offline support with service workers
- Advanced filtering and search capabilities
- Message editing and deletion
- Conversation archiving and restoration

## Version History

- **1.0.0**: Initial implementation with core chat functionality
- **1.1.0**: Added comprehensive error handling and type guards
- **1.2.0**: Enhanced logging and added usage examples
- **1.3.0**: Added comprehensive test coverage

## Support

For issues and questions:
- Check the troubleshooting section
- Review the test cases for examples
- Consult the existing frontend patterns
- Contact the development team for advanced support