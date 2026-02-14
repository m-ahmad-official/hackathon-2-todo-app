import { log_operation } from "./logging";

/**
 * Custom error classes for different types of errors
 */
export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ValidationError";
  }
}

export class AuthenticationError extends Error {
  constructor(message: string = "Authentication failed") {
    super(message);
    this.name = "AuthenticationError";
  }
}

export class AuthorizationError extends Error {
  constructor(message: string = "Authorization failed") {
    super(message);
    this.name = "AuthorizationError";
  }
}

export class NetworkError extends Error {
  constructor(message: string = "Network request failed") {
    super(message);
    this.name = "NetworkError";
  }
}

export class ServerError extends Error {
  constructor(message: string = "Server error occurred") {
    super(message);
    this.name = "ServerError";
  }
}

/**
 * Error handler function that logs and processes errors
 */
export function handleError(
  error: any,
  operation: string,
  userId?: string,
  taskId?: string,
): Error {
  // Log the error with context
  log_operation(`ERROR_IN_${operation.toUpperCase()}`, userId, taskId);

  // Determine error type and create appropriate error object
  if (error instanceof ValidationError) {
    log_operation(
      `VALIDATION_ERROR_IN_${operation.toUpperCase()}`,
      userId,
      taskId,
    );
    return error;
  } else if (error instanceof AuthenticationError) {
    log_operation(
      `AUTHENTICATION_ERROR_IN_${operation.toUpperCase()}`,
      userId,
      taskId,
    );
    return error;
  } else if (error instanceof AuthorizationError) {
    log_operation(
      `AUTHORIZATION_ERROR_IN_${operation.toUpperCase()}`,
      userId,
      taskId,
    );
    return error;
  } else if (error instanceof NetworkError) {
    log_operation(
      `NETWORK_ERROR_IN_${operation.toUpperCase()}`,
      userId,
      taskId,
    );
    return error;
  } else if (error instanceof ServerError) {
    log_operation(`SERVER_ERROR_IN_${operation.toUpperCase()}`, userId, taskId);
    return error;
  }

  // Handle HTTP errors
  if (error.response) {
    const status = error.response.status;

    switch (status) {
      case 400:
        log_operation(
          `BAD_REQUEST_ERROR_IN_${operation.toUpperCase()}`,
          userId,
          taskId,
        );
        return new ValidationError(
          `Bad request: ${error.response.data?.message || "Request validation failed"}`,
        );
      case 401:
        log_operation(
          `UNAUTHORIZED_ERROR_IN_${operation.toUpperCase()}`,
          userId,
          taskId,
        );
        return new AuthenticationError("Unauthorized access - please log in");
      case 403:
        log_operation(
          `FORBIDDEN_ERROR_IN_${operation.toUpperCase()}`,
          userId,
          taskId,
        );
        return new AuthorizationError(
          "Access forbidden - insufficient permissions",
        );
      case 404:
        log_operation(
          `NOT_FOUND_ERROR_IN_${operation.toUpperCase()}`,
          userId,
          taskId,
        );
        return new Error(
          `Resource not found: ${error.response.data?.message || "Requested resource does not exist"}`,
        );
      case 500:
        log_operation(
          `INTERNAL_SERVER_ERROR_IN_${operation.toUpperCase()}`,
          userId,
          taskId,
        );
        return new ServerError("Internal server error occurred");
      default:
        log_operation(
          `HTTP_ERROR_${status}_IN_${operation.toUpperCase()}`,
          userId,
          taskId,
        );
        return new Error(
          `HTTP Error ${status}: ${error.response.data?.message || "An error occurred"}`,
        );
    }
  }

  // Handle network errors (no response)
  if (error.request) {
    log_operation(
      `NETWORK_ERROR_IN_${operation.toUpperCase()}`,
      userId,
      taskId,
    );
    return new NetworkError("Network request failed - check connection");
  }

  // Handle other errors
  log_operation(`GENERAL_ERROR_IN_${operation.toUpperCase()}`, userId, taskId);
  return new Error(error.message || "An unexpected error occurred");
}

/**
 * Error boundary component for handling React errors
 */
export class ErrorHandler {
  /**
   * Handle async operations with error catching and logging
   */
  static async handleAsyncOperation<T>(
    operation: () => Promise<T>,
    operationName: string,
    userId?: string,
    taskId?: string,
  ): Promise<T> {
    try {
      log_operation(`STARTING_${operationName.toUpperCase()}`, userId, taskId);
      const result = await operation();
      log_operation(
        `SUCCESSFUL_${operationName.toUpperCase()}`,
        userId,
        taskId,
      );
      return result;
    } catch (error) {
      const handledError = handleError(error, operationName, userId, taskId);
      log_operation(`FAILED_${operationName.toUpperCase()}`, userId, taskId);
      throw handledError;
    }
  }

  /**
   * Handle synchronous operations with error catching and logging
   */
  static handleSyncOperation<T>(
    operation: () => T,
    operationName: string,
    userId?: string,
    taskId?: string,
  ): T {
    try {
      log_operation(`STARTING_${operationName.toUpperCase()}`, userId, taskId);
      const result = operation();
      log_operation(
        `SUCCESSFUL_${operationName.toUpperCase()}`,
        userId,
        taskId,
      );
      return result;
    } catch (error) {
      const handledError = handleError(error, operationName, userId, taskId);
      log_operation(`FAILED_${operationName.toUpperCase()}`, userId, taskId);
      throw handledError;
    }
  }
}

/**
 * Global error handler for uncaught errors
 */
export function setupGlobalErrorHandler(): void {
  // Handle uncaught promise rejections
  window.addEventListener("unhandledrejection", (event) => {
    log_operation("UNHANDLED_PROMISE_REJECTION", undefined, undefined);
    console.error("Unhandled promise rejection:", event.reason);
  });

  // Handle uncaught errors
  window.addEventListener("error", (event) => {
    log_operation("UNCAUGHT_ERROR", undefined, undefined);
    console.error("Uncaught error:", event.error);
  });
}

// Export the error handler functions
export default {
  ValidationError,
  AuthenticationError,
  AuthorizationError,
  NetworkError,
  ServerError,
  handleError,
  ErrorHandler,
  setupGlobalErrorHandler,
};
