import { chatApiService } from "./chat-api";
import { log_operation } from "../lib/logging";

/**
 * Chat API Usage Examples
 * Demonstrates how to use the chat API client in different scenarios
 */

class ChatApiExamples {
  /**
   * Example: Creating a new conversation
   */
  static async exampleCreateConversation() {
    try {
      log_operation("EXAMPLE_START", "Creating conversation");

      const request = {
        title: "My First AI Conversation",
      };

      const response = await chatApiService.createChatConversation(request);

      if (response.success && response.data) {
        log_operation(
          "EXAMPLE_SUCCESS",
          `Conversation created: ${response.data.id}`,
        );
        return response.data;
      } else {
        log_operation(
          "EXAMPLE_ERROR",
          response.error?.message || "Unknown error",
        );
        throw new Error(
          response.error?.message || "Failed to create conversation",
        );
      }
    } catch (error) {
      log_operation("EXAMPLE_ERROR", (error as Error).message);
      throw error;
    }
  }

  /**
   * Example: Listing all conversations
   */
  static async exampleListConversations() {
    try {
      log_operation("EXAMPLE_START", "Listing conversations");

      const response = await chatApiService.listConversations({
        limit: 20,
        offset: 0,
      });

      if (response.success && response.data) {
        log_operation(
          "EXAMPLE_SUCCESS",
          `Found ${response.data.length} conversations`,
        );

        // Example of rendering conversations
        response.data.forEach((conversation) => {
          console.log(
            `- ${conversation.id}: ${conversation.title || "Untitled"} (${conversation.messageCount} messages)`,
          );
        });

        return response.data;
      } else {
        log_operation(
          "EXAMPLE_ERROR",
          response.error?.message || "Unknown error",
        );
        throw new Error(
          response.error?.message || "Failed to list conversations",
        );
      }
    } catch (error) {
      log_operation("EXAMPLE_ERROR", (error as Error).message);
      throw error;
    }
  }

  /**
   * Example: Getting a specific conversation
   */
  static async exampleGetConversation(conversationId: number) {
    try {
      log_operation("EXAMPLE_START", `Getting conversation ${conversationId}`);

      const response = await chatApiService.getConversation({
        conversationId,
      });

      if (response.success && response.data) {
        log_operation(
          "EXAMPLE_SUCCESS",
          `Conversation found: ${response.data.title}`,
        );

        // Example of using conversation data
        console.log(`Conversation details:`);
        console.log(`ID: ${response.data.id}`);
        console.log(`Title: ${response.data.title || "Untitled"}`);
        console.log(`Created: ${response.data.createdAt}`);
        console.log(`Messages: ${response.data.messageCount}`);

        return response.data;
      } else {
        log_operation(
          "EXAMPLE_ERROR",
          response.error?.message || "Unknown error",
        );
        throw new Error(
          response.error?.message || "Failed to get conversation",
        );
      }
    } catch (error) {
      log_operation("EXAMPLE_ERROR", (error as Error).message);
      throw error;
    }
  }

  /**
   * Example: Adding a message to a conversation
   */
  static async exampleAddMessage(conversationId: number, content: string) {
    try {
      log_operation(
        "EXAMPLE_START",
        `Adding message to conversation ${conversationId}`,
      );

      const response = await chatApiService.addMessage({
        conversationId,
        content,
        metadata: {
          example: "This is test metadata",
        },
      });

      if (response.success && response.data) {
        log_operation("EXAMPLE_SUCCESS", `Message added: ${response.data.id}`);

        // Example of using message data
        console.log(`Message details:`);
        console.log(`ID: ${response.data.id}`);
        console.log(`Sender: ${response.data.sender}`);
        console.log(`Content: ${response.data.content}`);
        console.log(`Created: ${response.data.createdAt}`);

        return response.data;
      } else {
        log_operation(
          "EXAMPLE_ERROR",
          response.error?.message || "Unknown error",
        );
        throw new Error(response.error?.message || "Failed to add message");
      }
    } catch (error) {
      log_operation("EXAMPLE_ERROR", (error as Error).message);
      throw error;
    }
  }

  /**
   * Example: Getting messages from a conversation
   */
  static async exampleGetMessages(conversationId: number) {
    try {
      log_operation(
        "EXAMPLE_START",
        `Getting messages from conversation ${conversationId}`,
      );

      const response = await chatApiService.getMessages(conversationId, 20);

      if (response.success && response.data) {
        log_operation(
          "EXAMPLE_SUCCESS",
          `Found ${response.data.length} messages`,
        );

        // Example of rendering messages
        response.data.forEach((message, index) => {
          console.log(`\nMessage ${index + 1}:`);
          console.log(`Sender: ${message.sender}`);
          console.log(`Content: ${message.content}`);
          console.log(`Created: ${message.createdAt}`);

          if (message.metadata) {
            console.log(`Metadata:`, message.metadata);
          }
        });

        return response.data;
      } else {
        log_operation(
          "EXAMPLE_ERROR",
          response.error?.message || "Unknown error",
        );
        throw new Error(response.error?.message || "Failed to get messages");
      }
    } catch (error) {
      log_operation("EXAMPLE_ERROR", (error as Error).message);
      throw error;
    }
  }

  /**
   * Example: Deleting a conversation
   */
  static async exampleDeleteConversation(conversationId: number) {
    try {
      log_operation("EXAMPLE_START", `Deleting conversation ${conversationId}`);

      const response = await chatApiService.deleteConversation({
        conversationId,
      });

      if (response.success) {
        log_operation(
          "EXAMPLE_SUCCESS",
          `Conversation ${conversationId} deleted successfully`,
        );
        return true;
      } else {
        log_operation(
          "EXAMPLE_ERROR",
          response.error?.message || "Unknown error",
        );
        throw new Error(
          response.error?.message || "Failed to delete conversation",
        );
      }
    } catch (error) {
      log_operation("EXAMPLE_ERROR", (error as Error).message);
      throw error;
    }
  }

  /**
   * Example: Complete chat workflow
   */
  static async exampleCompleteChatWorkflow() {
    try {
      log_operation("EXAMPLE_START", "Complete chat workflow");

      // 1. Create a conversation
      const conversation = await this.exampleCreateConversation();

      if (!conversation) throw new Error("Failed to create conversation");

      // 2. Add a user message
      await this.exampleAddMessage(
        conversation.id,
        "Hello, I need help with my project",
      );

      // 3. Simulate AI response (in real app, this would come from the backend)
      console.log("\n[Simulated AI Response]");
      console.log(
        "Sure, I'd be happy to help! What specific aspect of your project do you need assistance with?",
      );

      // 4. Add AI message to conversation
      await this.exampleAddMessage(
        conversation.id,
        "Sure, I'd be happy to help! What specific aspect of your project do you need assistance with?",
      );

      // 5. Get all messages
      const messages = await this.exampleGetMessages(conversation.id);

      // 6. List conversations to show it's included
      await this.exampleListConversations();

      log_operation(
        "EXAMPLE_SUCCESS",
        "Complete chat workflow finished successfully",
      );
      return { conversation, messages };
    } catch (error) {
      log_operation("EXAMPLE_ERROR", (error as Error).message);
      throw error;
    }
  }
}

// Export the examples for use in the application
export const chatApiExamples = ChatApiExamples;
export default ChatApiExamples;
