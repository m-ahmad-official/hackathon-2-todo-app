/**
 * Logging utility functions for the frontend application
 */

interface LogContext {
  timestamp: string;
  level: string;
  operation: string;
  context?: string;
  userId?: string;
  taskId?: string;
  errorMessage?: string;
}

/**
 * Log an operation with context
 */
export function log_operation(
  operation: string,
  context?: string,
  error_message?: string,
): void {
  const timestamp = new Date().toISOString();
  const logEntry: LogContext = {
    timestamp,
    level: error_message ? "ERROR" : "INFO",
    operation,
    ...(context && { context }),
    ...(error_message && { errorMessage: error_message }),
  };

  console.log(JSON.stringify(logEntry));
}

/**
 * Log an error with operation context
 */
export function log_error(error: Error, operation: string): void {
  const timestamp = new Date().toISOString();
  const logEntry: LogContext = {
    timestamp,
    level: "ERROR",
    operation: `ERROR_IN_${operation}`,
    errorMessage: error.message,
  };

  console.error(JSON.stringify(logEntry));
}

/**
 * Log authentication events
 */
export function log_authentication_event(
  event: string,
  user_id?: string,
  ip_address?: string,
): void {
  const timestamp = new Date().toISOString();
  const logEntry: LogContext = {
    timestamp,
    level: "INFO",
    operation: `AUTH_${event.toUpperCase()}`,
    ...(user_id && { userId: user_id }),
    ...(ip_address && { context: `IP: ${ip_address}` }),
  };

  console.log(JSON.stringify(logEntry));
}

/**
 * Log authorization decisions
 */
export function log_authorization_decision(
  action: string,
  user_id: string,
  resource: string,
  granted: boolean,
): void {
  const timestamp = new Date().toISOString();
  const decision = granted ? "GRANTED" : "DENIED";
  const logEntry: LogContext = {
    timestamp,
    level: granted ? "INFO" : "WARN",
    operation: `AUTHORIZATION_${decision.toUpperCase()}`,
    context: `${action} access to ${resource} for user ${user_id}`,
  };

  console.log(JSON.stringify(logEntry));
}

/**
 * Log token validation results
 */
export function log_token_validation_result(
  token_status: string,
  user_id?: string,
  reason?: string,
): void {
  const timestamp = new Date().toISOString();
  const logEntry: LogContext = {
    timestamp,
    level:
      token_status.includes("INVALID") || token_status.includes("EXPIRED")
        ? "WARN"
        : "INFO",
    operation: `TOKEN_${token_status.toUpperCase()}`,
    ...(user_id && { userId: user_id }),
    ...(reason && { context: `Reason: ${reason}` }),
  };

  console.log(JSON.stringify(logEntry));
}

/**
 * Log token lifecycle events
 */
export function log_token_lifecycle_event(
  event: string,
  user_id?: string,
  token_id?: string,
  details?: string,
): void {
  const timestamp = new Date().toISOString();
  const logEntry: LogContext = {
    timestamp,
    level: "INFO",
    operation: `TOKEN_LIFECYCLE_${event.toUpperCase()}`,
    ...(user_id && { userId: user_id }),
    ...(token_id && { context: `Token: ${token_id}` }),
    ...(details && { context: details }),
  };

  console.log(JSON.stringify(logEntry));
}

/**
 * Log security events
 */
export function log_security_event(
  event: string,
  user_id?: string,
  ip_address?: string,
  severity: string = "INFO",
): void {
  const timestamp = new Date().toISOString();
  const logEntry: LogContext = {
    timestamp,
    level: severity,
    operation: `SECURITY_${event.toUpperCase()}`,
    ...(user_id && { userId: user_id }),
    ...(ip_address && { context: `IP: ${ip_address}` }),
  };

  if (severity === "ERROR" || severity === "CRITICAL") {
    console.error(JSON.stringify(logEntry));
  } else {
    console.log(JSON.stringify(logEntry));
  }
}
