import {
  log_token_lifecycle_event,
  log_authentication_event,
  log_security_event,
} from "../lib/logging";

interface TokenPayload {
  user_id: string;
  role: string;
  exp?: number;
  iat?: number;
}

class AuthService {
  /**
   * Get the current authentication token from storage
   */
  static getToken(): string | null {
    if (typeof window !== "undefined") {
      return localStorage.getItem("auth_token");
    }
    return null;
  }

  /**
   * Save the authentication token to storage
   */
  static saveToken(token: string): void {
    if (typeof window !== "undefined") {
      localStorage.setItem("auth_token", token);
      log_token_lifecycle_event("SAVED", undefined, "auth_token");
    }
  }

  /**
   * Remove the authentication token from storage
   */
  static removeToken(): void {
    if (typeof window !== "undefined") {
      localStorage.removeItem("auth_token");
      log_token_lifecycle_event("REMOVED", undefined, "auth_token");
    }
  }

  /**
   * Check if the current token is expired
   */
  static isTokenExpired(): boolean {
    const token = this.getToken();
    if (!token) {
      return true;
    }

    try {
      // Decode the token without verification to check expiration
      const parts = token.split(".");
      if (parts.length !== 3) {
        return true;
      }

      const payload: TokenPayload = JSON.parse(atob(parts[1]));
      const currentTime = Math.floor(Date.now() / 1000);

      if (payload.exp && payload.exp < currentTime) {
        log_token_lifecycle_event(
          "EXPIRED_CHECK",
          payload.user_id,
          undefined,
          "Token expired",
        );
        return true;
      }

      return false;
    } catch (error) {
      log_security_event("TOKEN_DECODE_ERROR", undefined, undefined, "ERROR");
      return true;
    }
  }

  /**
   * Refresh the authentication token
   * Note: In a real implementation, this would make an API call to refresh the token
   */
  static async refreshToken(): Promise<string | null> {
    log_token_lifecycle_event(
      "REFRESH_STARTED",
      undefined,
      undefined,
      "Starting token refresh process",
    );

    const token = this.getToken();
    if (!token) {
      log_authentication_event("REFRESH_FAILED_NO_TOKEN");
      return null;
    }

    // In a real implementation, this would make an API call to refresh the token
    // For now, we'll just return null to indicate refresh is needed
    log_token_lifecycle_event(
      "REFRESH_NEEDED",
      undefined,
      undefined,
      "Token refresh required - redirect to login",
    );

    // In a real app, you'd have a refresh token stored separately
    // and make an API call to get a new access token
    return null;
  }

  /**
   * Get the current user ID from the token
   */
  static getCurrentUserId(): string | null {
    const token = this.getToken();
    if (!token) {
      return null;
    }

    try {
      // Decode the token without verification to get user ID
      const parts = token.split(".");
      if (parts.length !== 3) {
        return null;
      }

      const payload: TokenPayload = JSON.parse(atob(parts[1]));
      return payload.user_id || null;
    } catch (error) {
      log_security_event("PAYLOAD_DECODE_ERROR", undefined, undefined, "ERROR");
      return null;
    }
  }

  /**
   * Get the full token payload
   */
  static getTokenPayload(): TokenPayload | null {
    const token = this.getToken();
    if (!token) {
      return null;
    }

    try {
      // Decode the token without verification
      const parts = token.split(".");
      if (parts.length !== 3) {
        return null;
      }

      const payload: TokenPayload = JSON.parse(atob(parts[1]));
      return payload;
    } catch (error) {
      log_security_event("PAYLOAD_PARSE_ERROR", undefined, undefined, "ERROR");
      return null;
    }
  }

  /**
   * Check if the user is authenticated
   */
  static isAuthenticated(): boolean {
    const token = this.getToken();
    if (!token) {
      return false;
    }

    // Check if token is expired
    return !this.isTokenExpired();
  }

  /**
   * Perform logout by removing the token and clearing user data
   */
  static logout(): void {
    this.removeToken();

    // Clear any other user-specific data
    if (typeof window !== "undefined") {
      sessionStorage.clear();
    }

    log_authentication_event(
      "LOGGED_OUT",
      this.getCurrentUserId() ?? undefined,
    );
  }

  /**
   * Validate the token and return user info if valid
   */
  static validateToken(): { isValid: boolean; userId?: string; role?: string } {
    if (!this.isAuthenticated()) {
      return { isValid: false };
    }

    const payload = this.getTokenPayload();
    if (!payload) {
      return { isValid: false };
    }

    log_authentication_event("TOKEN_VALIDATED", payload.user_id);
    return {
      isValid: true,
      userId: payload.user_id,
      role: payload.role,
    };
  }
}

export default AuthService;
