import axios from "axios";
import { apiClient } from "../services/api-client";
import { log_operation } from "../lib/logging";

/**
 * Chat API Models and Types
 */

// Message Types
export interface Message {
  id: number;
  conversationId: number;
  content: string;
  sender: "user" | "ai";
  createdAt: string;
  metadata?: Record<string, unknown>;
}

// Conversation Types
export interface Conversation {
  id: number;
  userId: string;
  title?: string;
  createdAt: string;
  updatedAt: string;
  messageCount: number;
  lastMessage?: string;
}

// Create Conversation Request
export interface CreateConversationRequest {
  title?: string;
}

// Get Conversation Request
export interface GetConversationRequest {
  conversationId: number;
}

// List Conversations Request
export interface ListConversationsRequest {
  limit?: number;
  offset?: number;
}

// Delete Conversation Request
export interface DeleteConversationRequest {
  conversationId: number;
}

// Add Message Request
export interface AddMessageRequest {
  conversationId: number;
  content: string;
  metadata?: Record<string, unknown>;
}

// AI Chat Request
export interface ChatRequest {
  message: string;
  conversationId?: number;
}

// AI Chat Response
export interface ChatResponse {
  conversationId: number;
  message: string;
  contextMetadata: {
    tasksModified: number;
    actionTaken: boolean;
    toolCalls: Array<{
      tool: string;
      success: boolean;
    }>;
  };
}

// Chat API Error Types
export interface ChatApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ChatApiError;
  timestamp: string;
}

/**
 * Chat API Service
 * Handles all chat-related API operations
 */
class ChatApiService {
  /**
   * Create a new chat conversation
   */
  async createChatConversation(
    request: CreateConversationRequest,
  ): Promise<ApiResponse<Conversation>> {
    try {
      log_operation("CHAT_CREATE_CONVERSATION_START", request.title);

      const response = await apiClient.post<ApiResponse<Conversation>>(
        "/conversations",
        request,
      );

      log_operation(
        "CHAT_CREATE_CONVERSATION_SUCCESS",
        String(response.data?.data?.id),
      );
      return response.data;
    } catch (error) {
      log_operation("CHAT_CREATE_CONVERSATION_ERROR", (error as Error).message);
      throw this.handleApiError(error);
    }
  }

  /**
   * Get a specific conversation
   */
  async getConversation(
    request: GetConversationRequest,
  ): Promise<ApiResponse<Conversation>> {
    try {
      log_operation(
        "CHAT_GET_CONVERSATION_START",
        String(request.conversationId),
      );

      const response = await apiClient.get<ApiResponse<Conversation>>(
        `/conversations/${request.conversationId}`,
      );

      log_operation(
        "CHAT_GET_CONVERSATION_SUCCESS",
        String(request.conversationId),
      );
      return response.data;
    } catch (error) {
      log_operation("CHAT_GET_CONVERSATION_ERROR", (error as Error).message);
      throw this.handleApiError(error);
    }
  }

  /**
   * List all conversations for the current user
   */
  async listConversations(
    request: ListConversationsRequest = {},
  ): Promise<ApiResponse<Conversation[]>> {
    try {
      log_operation("CHAT_LIST_CONVERSATIONS_START");

      const response = await apiClient.get<ApiResponse<Conversation[]>>(
        "/conversations",
        { params: request },
      );

      log_operation(
        "CHAT_LIST_CONVERSATIONS_SUCCESS",
        String(response.data?.data?.length),
      );
      return response.data;
    } catch (error) {
      log_operation("CHAT_LIST_CONVERSATIONS_ERROR", (error as Error).message);
      throw this.handleApiError(error);
    }
  }

  /**
   * Delete a conversation
   */
  async deleteConversation(
    request: DeleteConversationRequest,
  ): Promise<ApiResponse<void>> {
    try {
      log_operation(
        "CHAT_DELETE_CONVERSATION_START",
        String(request.conversationId),
      );

      const response = await apiClient.delete(
        `/conversations/${request.conversationId}`,
      );

      log_operation(
        "CHAT_DELETE_CONVERSATION_SUCCESS",
        String(request.conversationId),
      );

      // Transform the response to match ApiResponse format
      return {
        success: true,
        data: undefined,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      log_operation("CHAT_DELETE_CONVERSATION_ERROR", (error as Error).message);
      throw this.handleApiError(error);
    }
  }

  /**
   * Add a message to a conversation
   */
  async addMessage(request: AddMessageRequest): Promise<ApiResponse<Message>> {
    try {
      log_operation("CHAT_ADD_MESSAGE_START", String(request.conversationId));

      const response = await apiClient.post<ApiResponse<Message>>(
        `/conversations/${request.conversationId}/messages`,
        {
          content: request.content,
          metadata: request.metadata,
        },
      );

      log_operation("CHAT_ADD_MESSAGE_SUCCESS", String(request.conversationId));
      return response.data;
    } catch (error) {
      log_operation("CHAT_ADD_MESSAGE_ERROR", (error as Error).message);
      throw this.handleApiError(error);
    }
  }

  /**
   * Get messages from a conversation
   */
  async getMessages(
    conversationId: number,
    limit: number = 20,
  ): Promise<ApiResponse<Message[]>> {
    try {
      log_operation("CHAT_GET_MESSAGES_START", String(conversationId));

      const response = await apiClient.get<ApiResponse<Message[]>>(
        `/conversations/${conversationId}/messages`,
        { params: { limit } },
      );

      log_operation("CHAT_GET_MESSAGES_SUCCESS", String(conversationId));
      return response.data;
    } catch (error) {
      log_operation("CHAT_GET_MESSAGES_ERROR", (error as Error).message);
      throw this.handleApiError(error);
    }
  }

  /**
   * Send a chat message to the AI agent
   */
  async sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      log_operation(
        "CHAT_SEND_MESSAGE_START",
        request.conversationId ? String(request.conversationId) : undefined,
      );

      const response = await apiClient.post<ChatResponse>(
        "/chat/chat",
        request,
      );

      log_operation(
        "CHAT_SEND_MESSAGE_SUCCESS",
        String(response.data?.conversationId),
      );
      return response.data;
    } catch (error) {
      log_operation("CHAT_SEND_MESSAGE_ERROR", (error as Error).message);
      throw this.handleApiError(error);
    }
  }

  /**
   * Handle API errors and format them consistently
   */
  public handleApiError(error: unknown): ChatApiError {
    if (axios.isAxiosError(error)) {
      const response = error.response;
      if (response?.data) {
        return {
          code: response.data.error?.code || "API_ERROR",
          message: response.data.error?.message || error.message,
          details: response.data.error?.details,
        };
      }
    }

    return {
      code: "UNKNOWN_ERROR",
      message: (error as Error).message || "An unknown error occurred",
    };
  }

  /**
   * Check if the error is an authentication error
   */
  isAuthenticationError(error: ChatApiError): boolean {
    return [
      "UNAUTHORIZED",
      "INVALID_TOKEN",
      "TOKEN_EXPIRED",
      "AUTHENTICATION_REQUIRED",
    ].includes(error.code);
  }

  /**
   * Check if the error is a validation error
   */
  isValidationError(error: ChatApiError): boolean {
    return error.code === "VALIDATION_ERROR" || error.code === "BAD_REQUEST";
  }

  /**
   * Check if the error is a not found error
   */
  isNotFoundError(error: ChatApiError): boolean {
    return error.code === "NOT_FOUND";
  }
}

// Create a singleton instance
export const chatApiService = new ChatApiService();
export default ChatApiService;
