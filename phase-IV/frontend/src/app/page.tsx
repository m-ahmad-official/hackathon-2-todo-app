"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../providers/AuthProvider";
import Link from "next/link";

export default function HomePage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h1 className="mt-6 text-center text-4xl font-extrabold text-gray-900">
            Todo Application
          </h1>
          <p className="mt-2 text-center text-sm text-gray-600 max-w-2xl mx-auto">
            A secure, full-stack task management application with user authentication and data isolation
          </p>
        </div>
        <div className="flex flex-col items-center gap-6">
          <p className="text-gray-600 text-center max-w-md">
            Sign in to access your tasks or create an account to get started with your personal task management
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <Link
              href="/sign-in"
              className="rounded-md bg-blue-600 px-6 py-3 text-white font-medium hover:bg-blue-700 transition-colors text-center"
            >
              Sign In
            </Link>
            <Link
              href="/sign-up"
              className="rounded-md border border-blue-600 px-6 py-3 text-blue-600 font-medium hover:bg-blue-50 dark:hover:bg-gray-700 transition-colors text-center"
            >
              Create Account
            </Link>
          </div>
        </div>
        <div className="mt-12 pt-8 border-t border-gray-200 dark:border-gray-700 w-full max-w-md">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Features</h3>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-3 text-left text-gray-600 dark:text-gray-400">
            <li className="flex items-center gap-2">
              <svg className="h-5 w-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
              </svg>
              Secure authentication
            </li>
            <li className="flex items-center gap-2">
              <svg className="h-5 w-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
              </svg>
              User data isolation
            </li>
            <li className="flex items-center gap-2">
              <svg className="h-5 w-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
              </svg>
              Task CRUD operations
            </li>
            <li className="flex items-center gap-2">
              <svg className="h-5 w-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
              </svg>
              Responsive design
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
