"use client";

import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";
import { useRouter } from "next/navigation";
import { authApiService } from "../services/auth-api";
import { log_operation } from "../lib/logging";

interface AuthUser {
  id: string;
  name?: string;
  email?: string;
  role?: string;
}

interface AuthContextType {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: { email: string; password: string }) => Promise<boolean>;
  logout: () => void;
  signup: (userData: {
    email: string;
    password: string;
    name: string;
  }) => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | null>(null);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const router = useRouter();

  useEffect(() => {
    // Check authentication status on initial load
    const checkAuthStatus = () => {
      try {
        const token = localStorage.getItem("auth_token");
        if (token) {
          // In a real app, we would verify the token here via API call
          // For now, we'll decode the token to get user info
          try {
            const parts = token.split(".");
            if (parts.length === 3) {
              const payload = JSON.parse(atob(parts[1]));
              setUser({
                id: payload.user_id || "unknown",
                email: payload.email,
                name: payload.name,
                role: payload.role || "user",
              });
              setIsAuthenticated(true);
            }
          } catch (error) {
            console.error("Error decoding token:", error);
            localStorage.removeItem("auth_token");
          }
        }
      } catch (error) {
        console.error("Error checking auth status:", error);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  const login = async (credentials: {
    email: string;
    password: string;
  }): Promise<boolean> => {
    try {
      log_operation("AUTH_PROVIDER_LOGIN_START", credentials.email);

      // Call the auth API service to login
      const response = await authApiService.login(credentials);

      // Save the token
      localStorage.setItem("auth_token", response.access_token);

      // Set user data
      setUser({
        id: response.user.id.toString(),
        email: response.user.email,
        name: response.user.name,
        role: "user",
      });

      setIsAuthenticated(true);

      log_operation("AUTH_PROVIDER_LOGIN_SUCCESS", credentials.email);
      router.push("/dashboard");
      return true;
    } catch (error) {
      log_operation(
        "AUTH_PROVIDER_LOGIN_ERROR",
        credentials.email,
        (error as Error).message,
      );
      console.error("Login error:", error);
      return false;
    }
  };

  const logout = () => {
    try {
      localStorage.removeItem("auth_token");
      setUser(null);
      setIsAuthenticated(false);
      router.push("/sign-in");
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  const signup = async (userData: {
    email: string;
    password: string;
    name: string;
  }): Promise<boolean> => {
    try {
      log_operation("AUTH_PROVIDER_SIGNUP_START", userData.email);

      // Call the auth API service to register
      const response = await authApiService.register(userData);

      // Save the token
      localStorage.setItem("auth_token", response.access_token);

      // Set user data
      setUser({
        id: response.user.id.toString(),
        email: response.user.email,
        name: response.user.name,
        role: "user",
      });

      setIsAuthenticated(true);

      log_operation("AUTH_PROVIDER_SIGNUP_SUCCESS", userData.email);
      router.push("/dashboard");
      return true;
    } catch (error) {
      log_operation(
        "AUTH_PROVIDER_SIGNUP_ERROR",
        userData.email,
        (error as Error).message,
      );
      console.error("Signup error:", error);
      return false;
    }
  };

  const value = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    signup,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export default AuthProvider;
