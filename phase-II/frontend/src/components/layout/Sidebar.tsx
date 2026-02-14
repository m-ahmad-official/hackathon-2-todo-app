import React, { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/src/providers/AuthProvider";

const Sidebar: React.FC = () => {
  const [isExpanded, setIsExpanded] = useState(true);
  const { user, logout, isAuthenticated } = useAuth();

  // Toggle sidebar expanded/collapsed state
  const toggleSidebar = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div
      className={`${isExpanded ? "w-64" : "w-20"} bg-white shadow h-[calc(100vh-4rem)] sticky top-16 transition-all duration-300 ease-in-out`}
    >
      <div className="flex flex-col h-full">
        <div className="p-4 border-b">
          <div className="flex items-center justify-between">
            {isExpanded && (
              <h2 className="text-lg font-semibold text-gray-800">
                Navigation
              </h2>
            )}
            <button
              onClick={toggleSidebar}
              className="p-1 rounded-md hover:bg-gray-100 text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
              aria-label={isExpanded ? "Collapse sidebar" : "Expand sidebar"}
            >
              {isExpanded ? (
                <svg
                  className="h-5 w-5"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              ) : (
                <svg
                  className="h-5 w-5"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
            </button>
          </div>
        </div>

        <nav className="flex-1 px-2 py-4">
          <ul className="space-y-1">
            <li>
              <Link
                href="/dashboard"
                className="flex items-center p-2 text-base font-normal text-gray-900 rounded-lg hover:bg-gray-100 group"
              >
                <svg
                  className="w-5 h-5 text-gray-500 transition duration-75 group-hover:text-gray-900"
                  aria-hidden="true"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="currentColor"
                  viewBox="0 0 22 21"
                >
                  <path d="M16.975 11H10V4.025a1 1 0 0 0-1.066-.998 8.5 8.5 0 1 0 9.039 9.039.999.999 0 0 0-1-1.066h.002Z" />
                  <path d="M12.5 0c-.157 0-.311.01-.565.027A1 1 0 0 0 11 1.02V10h8.975a1 1 0 0 0 1-.935c.013-.188.028-.374.028-.565Z" />
                </svg>
                {isExpanded && <span className="ml-3">Dashboard</span>}
              </Link>
            </li>
            <li>
              <Link
                href="/tasks"
                className="flex items-center p-2 text-base font-normal text-gray-900 rounded-lg hover:bg-gray-100 group"
              >
                <svg
                  className="flex-shrink-0 w-5 h-5 text-gray-500 transition duration-75 group-hover:text-gray-900"
                  aria-hidden="true"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="currentColor"
                  viewBox="0 0 18 20"
                >
                  <path d="M17 5.923A1 1 0 0 0 16 5h-3V4a4 4 0 1 0-8 0v1H2a1 1 0 0 0-1 .923L.086 17.846A2 2 0 0 0 2.08 20h13.84a2 2 0 0 0 1.994-1.84l.086-12.077A1 1 0 0 0 17 5.923ZM7 9a1 1 0 0 1-2 0V7h2v2Zm0-5a2 2 0 1 1 4 0v1H7V4Zm6 5a1 1 0 1 1-2 0V7h2v2Z" />
                </svg>
                {isExpanded && (
                  <span className="flex-1 ml-3 whitespace-nowrap">
                    My Tasks
                  </span>
                )}
              </Link>
            </li>
            <li>
              <Link
                href="/completed"
                className="flex items-center p-2 text-base font-normal text-gray-900 rounded-lg hover:bg-gray-100 group"
              >
                <svg
                  className="flex-shrink-0 w-5 h-5 text-gray-500 transition duration-75 group-hover:text-gray-900"
                  aria-hidden="true"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="currentColor"
                  viewBox="0 0 20 18"
                >
                  <path d="M14 4a3.968 3.968 0 0 0-1.4.263 1 1 0 0 0-.566.804l.16.962c.162.972.3.964 1.2.964.857 0 2.7.026 3.5.026.9 0 1 0 1.2-.9A1 1 0 0 0 16 5.025c-.2-.2-.4-.263-.6-.263h-1.8Z" />
                  <path
                    d="M15.982 2.025H18a1 1 0 0 1 1 1v1a1 1 0 0 1-1 1h-.018a1 1 0 0 1-.982-.838l-.018-.162a1 1 0 0 0-.982-.838l-12.036-.025a1 1 0 0 0-.982.838l-.018.162a1 1 0 0 1-.982.838H1a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1h2.018a1 1 0 0 1 .982.838l.018.162a1 1 0 0 0 .982.838l12.036.025a1 1 0 0 0 .982-.838l.018-.162A1 1 0 0 1 15.982 2.025Z"
                    clipRule="evenodd"
                  />
                  <path d="M4 11a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v1a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1v-1Zm7-1a1 1 0 0 0-1 1v1a1 1 0 0 0 1 1h1a1 1 0 0 0 1-1v-1a1 1 0 0 0-1-1h-1Zm-7 6a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v1a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1v-1Zm7.982-.025H18a1 1 0 0 1 1 1v1a1 1 0 0 1-1 1h-5a1 1 0 0 1-1-1v-1a1 1 0 0 1 1-1h2.982Z" />
                </svg>
                {isExpanded && (
                  <span className="flex-1 ml-3 whitespace-nowrap">
                    Completed Tasks
                  </span>
                )}
              </Link>
            </li>
          </ul>
        </nav>

        <div className="p-4 border-t">
          {isAuthenticated && user ? (
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center">
                  <span className="text-indigo-800 font-medium">
                    {user.name?.charAt(0)?.toUpperCase() ||
                      user.id?.charAt(0)?.toUpperCase()}
                  </span>
                </div>
              </div>
              <div className="ml-3 overflow-hidden">
                {isExpanded && (
                  <>
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {user.name || user.id}
                    </p>
                    <p className="text-xs font-medium text-gray-500 truncate">
                      User
                    </p>
                  </>
                )}
              </div>
            </div>
          ) : (
            <div className="text-sm text-gray-500">
              {isExpanded && "Not logged in"}
            </div>
          )}

          {isAuthenticated && (
            <button
              onClick={logout}
              className={`mt-3 w-full text-left px-4 py-2 text-sm font-medium text-red-700 hover:text-red-900 ${!isExpanded ? "hidden" : ""}`}
            >
              Sign out
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
