'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import AuthService from '../services/auth-service';

interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  redirectTo = '/sign-in'
}) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Check if user is authenticated
        const authenticated = AuthService.isAuthenticated();
        setIsAuthenticated(authenticated);

        // If not authenticated, redirect to login
        if (!authenticated) {
          router.push(redirectTo);
        }
      } catch (error) {
        console.error('Error checking authentication:', error);
        setIsAuthenticated(false);
        router.push(redirectTo);
      }
    };

    checkAuth();
  }, [router, redirectTo]);

  // Show nothing while checking authentication status
  if (isAuthenticated === null) {
    return <div>Loading...</div>;
  }

  // If authenticated, render the protected content
  if (isAuthenticated) {
    return <>{children}</>;
  }

  // If not authenticated, we're redirecting (the redirect happens in useEffect)
  return null;
};

export default ProtectedRoute;