import { describe, it, expect, beforeEach, jest } from "@jest/globals";

// Mock the apiClient module BEFORE importing anything that uses it
const mockPost = jest.fn();
const mockGet = jest.fn();
const mockDelete = jest.fn();

jest.mock("../../services/api-client", () => ({
  apiClient: {
    post: mockPost,
    get: mockGet,
    delete: mockDelete,
    put: jest.fn(),
    patch: jest.fn(),
  },
}));

import {
  chatApiService,
  Conversation,
  Message,
  ApiResponse,
} from "../chat-api";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyMock = any;

describe("Chat API Service", () => {
  // Mock data
  const mockUser = {
    id: "test-user-123",
    email: "test@example.com",
  };

  const mockConversation: Conversation = {
    id: 1,
    userId: mockUser.id,
    title: "Test Conversation",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    messageCount: 0,
    lastMessage: undefined,
  };

  const mockMessage: Message = {
    id: 1,
    conversationId: 1,
    content: "Hello, this is a test message",
    sender: "user",
    createdAt: new Date().toISOString(),
    metadata: undefined,
  };

  const mockApiResponse = <T>(data: T): ApiResponse<T> => ({
    success: true,
    data,
    timestamp: new Date().toISOString(),
  });

  beforeEach(() => {
    // Reset all mocks to their initial state before each test
    jest.resetAllMocks();
  });

  describe("createChatConversation", () => {
    it("should create a conversation successfully", async () => {
      mockPost.mockResolvedValue({
        data: mockApiResponse(mockConversation),
      });

      const result = await chatApiService.createChatConversation({
        title: "Test Conversation",
      });

      expect(result.success).toBe(true);
      expect(result.data).toEqual(mockConversation);
    });

    it("should handle create conversation error", async () => {
      mockPost.mockRejectedValueOnce(new Error("Network error"));

      await expect(
        chatApiService.createChatConversation({ title: "Test" }),
      ).rejects.toMatchObject({ message: "Network error" });
    });
  });

  describe("getConversation", () => {
    it("should get a conversation successfully", async () => {
      mockGet.mockResolvedValue({
        data: mockApiResponse(mockConversation),
      });

      const result = await chatApiService.getConversation({
        conversationId: 1,
      });

      expect(result.success).toBe(true);
      expect(result.data).toEqual(mockConversation);
    });

    it("should handle get conversation error", async () => {
      mockGet.mockRejectedValueOnce(new Error("Conversation not found"));

      await expect(
        chatApiService.getConversation({ conversationId: 999 }),
      ).rejects.toMatchObject({ message: "Conversation not found" });
    });
  });

  describe("listConversations", () => {
    it("should list conversations successfully", async () => {
      mockGet.mockResolvedValue({
        data: mockApiResponse([mockConversation]),
      });

      const result = await chatApiService.listConversations({
        limit: 10,
        offset: 0,
      });

      expect(result.success).toBe(true);
      expect(Array.isArray(result.data)).toBe(true);
      expect(result.data?.length).toBe(1);
    });

    it("should handle list conversations error", async () => {
      mockGet.mockRejectedValueOnce(new Error("Failed to fetch conversations"));

      await expect(
        chatApiService.listConversations({ limit: 10 }),
      ).rejects.toMatchObject({ message: "Failed to fetch conversations" });
    });
  });

  describe("deleteConversation", () => {
    it("should delete a conversation successfully", async () => {
      mockDelete.mockResolvedValue({
        data: undefined,
      });

      const result = await chatApiService.deleteConversation({
        conversationId: 1,
      });

      expect(result.success).toBe(true);
      expect(result.data).toBeUndefined();
    });

    it("should handle delete conversation error", async () => {
      mockDelete.mockRejectedValueOnce(new Error("Failed to delete conversation"));

      await expect(
        chatApiService.deleteConversation({ conversationId: 1 }),
      ).rejects.toMatchObject({ message: "Failed to delete conversation" });
    });
  });

  describe("addMessage", () => {
    it("should add a message successfully", async () => {
      mockPost.mockResolvedValue({
        data: mockApiResponse(mockMessage),
      });

      const result = await chatApiService.addMessage({
        conversationId: 1,
        content: "Test message",
      });

      expect(result.success).toBe(true);
      expect(result.data).toEqual(mockMessage);
    });

    it("should handle add message error", async () => {
      mockPost.mockRejectedValueOnce(new Error("Failed to add message"));

      await expect(
        chatApiService.addMessage({
          conversationId: 1,
          content: "Test",
        }),
      ).rejects.toMatchObject({ message: "Failed to add message" });
    });
  });

  describe("getMessages", () => {
    it("should get messages successfully", async () => {
      mockGet.mockResolvedValue({
        data: mockApiResponse([mockMessage]),
      });

      const result = await chatApiService.getMessages(1, 20);

      expect(result.success).toBe(true);
      expect(Array.isArray(result.data)).toBe(true);
      expect(result.data?.length).toBe(1);
    });

    it("should handle get messages error", async () => {
      mockGet.mockRejectedValueOnce(
        new Error("Failed to fetch messages")
      );

      await expect(chatApiService.getMessages(1, 20)).rejects.toMatchObject(
        { message: "Failed to fetch messages" }
      );
    });
  });

  describe("Error Handling", () => {
    it("should handle API errors consistently", () => {
      const apiError = chatApiService.handleApiError(new Error("Test error"));

      expect(apiError.code).toBe("UNKNOWN_ERROR");
      expect(apiError.message).toBe("Test error");
    });

    it("should identify authentication errors", () => {
      const authError: any = {
        code: "UNAUTHORIZED",
        message: "Invalid token",
      };

      expect(chatApiService.isAuthenticationError(authError)).toBe(true);
    });

    it("should identify validation errors", () => {
      const validationError: any = {
        code: "VALIDATION_ERROR",
        message: "Invalid data",
      };

      expect(chatApiService.isValidationError(validationError)).toBe(true);
    });

    it("should identify not found errors", () => {
      const notFoundError: any = {
        code: "NOT_FOUND",
        message: "Resource not found",
      };

      expect(chatApiService.isNotFoundError(notFoundError)).toBe(true);
    });
  });

  describe("Logging", () => {
    it("should log operations during API calls", async () => {
      mockPost.mockResolvedValue({
        data: mockApiResponse(mockConversation),
      });

      const consoleSpy = jest
        .spyOn(console, "log")
        .mockImplementation(() => {});

      await chatApiService.createChatConversation({ title: "Test" });

      expect(consoleSpy).toHaveBeenCalled();
      consoleSpy.mockRestore();
    });
  });
});
