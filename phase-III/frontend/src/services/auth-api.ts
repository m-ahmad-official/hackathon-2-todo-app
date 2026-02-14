import { apiClient } from "./api-client";
import { log_operation } from "../lib/logging";

interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    name?: string;
  };
}

interface ValidateTokenResponse {
  valid: boolean;
  user_id: string;
  role: string;
  exp: number;
}

interface RefreshTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

interface LogoutResponse {
  revoked: boolean;
  message: string;
}

class AuthApiService {
  /**
   * Login a user and return JWT token
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    try {
      log_operation("AUTH_LOGIN_START", credentials.email);

      // Create form data for the login request
      const formData = new URLSearchParams();
      formData.append("email", credentials.email);
      formData.append("password", credentials.password);

      // For form data submission, we need to use fetch directly instead of axios
      // since our apiClient is configured for JSON
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1"}/login`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: formData,
        },
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `HTTP error! status: ${response.status}, message: ${errorText}`,
        );
      }

      const data = await response.json();
      log_operation("AUTH_LOGIN_SUCCESS", credentials.email);
      return data;
    } catch (error) {
      log_operation(
        "AUTH_LOGIN_ERROR",
        credentials.email,
        (error as Error).message,
      );
      throw error;
    }
  }

  /**
   * Register a new user
   */
  async register(userData: RegisterRequest): Promise<LoginResponse> {
    try {
      log_operation("AUTH_REGISTER_START", userData.email);

      // Create form data for the register request
      const formData = new URLSearchParams();
      formData.append("email", userData.email);
      formData.append("password", userData.password);
      formData.append("name", userData.name);

      // For form data submission, we need to use fetch directly instead of axios
      // since our apiClient is configured for JSON
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1"}/register`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: formData,
        },
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `HTTP error! status: ${response.status}, message: ${errorText}`,
        );
      }

      const data = await response.json();
      log_operation("AUTH_REGISTER_SUCCESS", userData.email);
      return data;
    } catch (error) {
      log_operation(
        "AUTH_REGISTER_ERROR",
        userData.email,
        (error as Error).message,
      );
      throw error;
    }
  }

  /**
   * Validate the current JWT token
   */
  async validateToken(): Promise<ValidateTokenResponse> {
    try {
      log_operation("AUTH_VALIDATE_TOKEN_START", "validation");

      // Make a GET request to the token validation endpoint
      const response =
        await apiClient.get<ValidateTokenResponse>("/token/validate");

      log_operation("AUTH_VALIDATE_TOKEN_SUCCESS", "validation");
      return response.data;
    } catch (error) {
      log_operation(
        "AUTH_VALIDATE_TOKEN_ERROR",
        "validation",
        (error as Error).message,
      );
      throw error;
    }
  }

  /**
   * Refresh the JWT token
   */
  async refreshToken(): Promise<RefreshTokenResponse> {
    try {
      log_operation("AUTH_REFRESH_TOKEN_START", "refresh");

      // Make a POST request to the token refresh endpoint
      const response =
        await apiClient.post<RefreshTokenResponse>("/token/refresh");

      log_operation("AUTH_REFRESH_TOKEN_SUCCESS", "refresh");
      return response.data;
    } catch (error) {
      log_operation(
        "AUTH_REFRESH_TOKEN_ERROR",
        "refresh",
        (error as Error).message,
      );
      throw error;
    }
  }

  /**
   * Logout user (revoke token)
   */
  async logout(): Promise<LogoutResponse> {
    try {
      log_operation("AUTH_LOGOUT_START", "logout");

      // Make a POST request to the token revoke endpoint
      const response = await apiClient.post<LogoutResponse>("/token/revoke");

      log_operation("AUTH_LOGOUT_SUCCESS", "logout");
      return response.data;
    } catch (error) {
      log_operation("AUTH_LOGOUT_ERROR", "logout", (error as Error).message);
      // Even if the server-side revoke fails, we should still clear local storage
      throw error;
    }
  }
}

export const authApiService = new AuthApiService();
export default AuthApiService;
