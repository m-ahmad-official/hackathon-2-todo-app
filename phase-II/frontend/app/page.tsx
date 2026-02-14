"use client";

import Link from "next/link";
import { useAuth } from "../src/providers/AuthProvider";

export default function Home() {
  const { isAuthenticated, user } = useAuth();

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 font-sans dark:bg-gray-900">
      <main className="flex min-h-screen w-full max-w-4xl flex-col items-center justify-between py-16 px-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
        <div className="flex flex-col items-center gap-8 text-center">
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Todo Application
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl">
              A secure, full-stack task management application with user
              authentication and data isolation
            </p>
          </div>

          {isAuthenticated && user ? (
            <div className="flex flex-col items-center gap-6">
              <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-200">
                Welcome back!
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                Your tasks are ready for management
              </p>
              <Link
                href="/dashboard"
                className="rounded-md bg-blue-600 px-6 py-3 text-white font-medium hover:bg-blue-700 transition-colors"
              >
                Go to Dashboard
              </Link>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-6">
              <p className="text-gray-600 dark:text-gray-400 max-w-md">
                Sign in to access your tasks or create an account to get started
                with your personal task management
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link
                  href="/sign-in"
                  className="rounded-md bg-blue-600 px-6 py-3 text-white font-medium hover:bg-blue-700 transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  href="/sign-up"
                  className="rounded-md border border-blue-600 px-6 py-3 text-blue-600 font-medium hover:bg-blue-50 dark:hover:bg-gray-700 transition-colors"
                >
                  Create Account
                </Link>
              </div>
            </div>
          )}

          <div className="mt-12 pt-8 border-t border-gray-200 dark:border-gray-700 w-full max-w-md">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Features
            </h3>
            <ul className="grid grid-cols-1 md:grid-cols-2 gap-3 text-left text-gray-600 dark:text-gray-400">
              <li className="flex items-center gap-2">
                <svg
                  className="h-5 w-5 text-green-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                Secure authentication
              </li>
              <li className="flex items-center gap-2">
                <svg
                  className="h-5 w-5 text-green-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                User data isolation
              </li>
              <li className="flex items-center gap-2">
                <svg
                  className="h-5 w-5 text-green-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                Task CRUD operations
              </li>
              <li className="flex items-center gap-2">
                <svg
                  className="h-5 w-5 text-green-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                Responsive design
              </li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
}
