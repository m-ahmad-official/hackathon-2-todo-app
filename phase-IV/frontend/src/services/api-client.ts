import axios, {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  AxiosError,
} from "axios";
import { log_operation } from "../lib/logging";

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    // Create axios instance with base configuration
    this.client = axios.create({
      baseURL:
        process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1",
      timeout: 10000, // 10 seconds timeout
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Add request interceptor to attach JWT token
    this.client.interceptors.request.use(
      (config) => {
        // Get the authentication token from localStorage
        const token =
          typeof window !== "undefined"
            ? localStorage.getItem("auth_token")
            : null;

        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
          log_operation("ATTACHING_JWT_TOKEN", "api-client");
        }

        return config;
      },
      (error) => {
        log_operation("REQUEST_INTERCEPTOR_ERROR", "api-client", error.message);
        return Promise.reject(error);
      },
    );

    // Add response interceptor to handle 401 responses
    this.client.interceptors.response.use(
      (response) => {
        return response;
      },
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          log_operation("RECEIVED_401_RESPONSE", "api-client");

          // Clear any stored auth data
          if (typeof window !== "undefined") {
            localStorage.removeItem("auth_token");
          }

          // Redirect to login page
          if (typeof window !== "undefined") {
            window.location.href = "/sign-in";
          }
        }

        return Promise.reject(error);
      },
    );
  }

  /**
   * Make a GET request
   */
  async get<T>(
    url: string,
    config?: AxiosRequestConfig,
  ): Promise<AxiosResponse<T>> {
    try {
      log_operation(`GET_REQUEST_START: ${url}`, "api-client");
      const response = await this.client.get<T>(url, config);
      log_operation(`GET_REQUEST_SUCCESS: ${url}`, "api-client");
      return response;
    } catch (error) {
      log_operation(
        `GET_REQUEST_ERROR: ${url}`,
        "api-client",
        (error as Error).message,
      );
      throw error;
    }
  }

  /**
   * Make a POST request
   */
  async post<TResponse, TData = unknown>(
    url: string,
    data?: TData,
    config?: AxiosRequestConfig,
  ): Promise<AxiosResponse<TResponse>> {
    try {
      log_operation(`POST_REQUEST_START: ${url}`, "api-client");
      const response = await this.client.post<TResponse>(url, data, config);
      log_operation(`POST_REQUEST_SUCCESS: ${url}`, "api-client");
      return response;
    } catch (error) {
      log_operation(
        `POST_REQUEST_ERROR: ${url}`,
        "api-client",
        (error as Error).message,
      );
      throw error;
    }
  }

  /**
   * Make a PUT request
   */
  async put<TResponse, TData = unknown>(
    url: string,
    data?: TData,
    config?: AxiosRequestConfig,
  ): Promise<AxiosResponse<TResponse>> {
    try {
      log_operation(`PUT_REQUEST_START: ${url}`, "api-client");
      const response = await this.client.put<TResponse>(url, data, config);
      log_operation(`PUT_REQUEST_SUCCESS: ${url}`, "api-client");
      return response;
    } catch (error) {
      log_operation(
        `PUT_REQUEST_ERROR: ${url}`,
        "api-client",
        (error as Error).message,
      );
      throw error;
    }
  }

  /**
   * Make a PATCH request
   */
  async patch<TResponse, TData = unknown>(
    url: string,
    data?: TData,
    config?: AxiosRequestConfig,
  ): Promise<AxiosResponse<TResponse>> {
    try {
      log_operation(`PATCH_REQUEST_START: ${url}`, "api-client");
      const response = await this.client.patch<TResponse>(url, data, config);
      log_operation(`PATCH_REQUEST_SUCCESS: ${url}`, "api-client");
      return response;
    } catch (error) {
      log_operation(
        `PATCH_REQUEST_ERROR: ${url}`,
        "api-client",
        (error as Error).message,
      );
      throw error;
    }
  }

  /**
   * Make a DELETE request
   */
  async delete(
    url: string,
    config?: AxiosRequestConfig,
  ): Promise<AxiosResponse<void>> {
    try {
      log_operation(`DELETE_REQUEST_START: ${url}`, "api-client");
      const response = await this.client.delete(url, config);
      log_operation(`DELETE_REQUEST_SUCCESS: ${url}`, "api-client");
      return response;
    } catch (error) {
      log_operation(
        `DELETE_REQUEST_ERROR: ${url}`,
        "api-client",
        (error as Error).message,
      );
      throw error;
    }
  }

  /**
   * Set a new base URL
   */
  setBaseURL(url: string): void {
    this.client.defaults.baseURL = url;
  }

  /**
   * Set default headers
   */
  setHeader(name: string, value: string): void {
    this.client.defaults.headers.common[name] = value;
  }

  /**
   * Remove a default header
   */
  removeHeader(name: string): void {
    delete this.client.defaults.headers.common[name];
  }
}

// Create a singleton instance
export const apiClient = new ApiClient();

// Export the class for potential multiple instances if needed
export default ApiClient;
