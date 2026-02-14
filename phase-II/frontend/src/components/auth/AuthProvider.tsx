'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import AuthService from '../../services/auth-service';

interface AuthUser {
  id: string;
  role: string;
}

interface AuthContextType {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string) => void;
  logout: () => void;
  refreshToken: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | null>(null);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    // Check authentication status on initial load
    const initAuth = async () => {
      try {
        const token = AuthService.getToken();
        if (token && !AuthService.isTokenExpired()) {
          const payload = AuthService.getTokenPayload();
          if (payload) {
            setUser({ id: payload.user_id, role: payload.role || 'user' });
            setIsAuthenticated(true);
          }
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();

    // Set up token expiration check interval
    const interval = setInterval(() => {
      // Check if token is expired
      if (AuthService.isTokenExpired()) {
        // Automatically log out user if token is expired
        handleLogout();
      }
    }, 60000); // Check every minute

    // Clean up interval on unmount
    return () => clearInterval(interval);
  }, []);

  const login = (token: string) => {
    AuthService.saveToken(token);
    const payload = AuthService.getTokenPayload();

    if (payload) {
      setUser({ id: payload.user_id, role: payload.role || 'user' });
      setIsAuthenticated(true);
    }
  };

  const handleLogout = () => {
    AuthService.logout();
    setUser(null);
    setIsAuthenticated(false);
  };

  const logout = () => {
    handleLogout();
  };

  const refreshToken = async (): Promise<boolean> => {
    try {
      const newToken = await AuthService.refreshToken();
      if (newToken) {
        AuthService.saveToken(newToken);
        const payload = AuthService.getTokenPayload();

        if (payload) {
          setUser({ id: payload.user_id, role: payload.role || 'user' });
          setIsAuthenticated(true);
          return true;
        }
      }
      return false;
    } catch (error) {
      console.error('Error refreshing token:', error);
      // If refresh fails, log out the user
      handleLogout();
      return false;
    }
  };

  const value = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    refreshToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthProvider;