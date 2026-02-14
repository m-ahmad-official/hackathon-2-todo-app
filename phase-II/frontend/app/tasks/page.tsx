"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "@/src/providers/AuthProvider";
import TaskList from "@/src/components/tasks/TaskList";
import TaskForm from "@/src/components/tasks/TaskForm";
import TaskService from "@/src/services/task-service";
import { TaskCreate, TaskResponse, TaskUpdate } from "@/src/models/task";

const TasksPage: React.FC = () => {
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [showForm, setShowForm] = useState<boolean>(false);
  const { user, isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      // Redirect would be handled by layout
      return;
    }

    if (isAuthenticated && user) {
      loadTasks();
    }
  }, [isAuthenticated, isLoading, user]);

  const loadTasks = async () => {
    if (!user) return;

    try {
      setLoading(true);
      // Get all tasks for the authenticated user
      const userTasks = await TaskService.getTasksByUserId(user.id);
      setTasks(userTasks);
    } catch (error) {
      console.error("Error loading tasks:", error);
      // In a real app, you'd show an error message to the user
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async (taskData: TaskCreate) => {
    try {
      const newTask = await TaskService.createTask(taskData);
      setTasks([...tasks, newTask]);
      setShowForm(false);
    } catch (error) {
      console.error("Error creating task:", error);
      // In a real app, you'd show an error message to the user
    }
  };

  const handleToggleCompletion = async (taskId: number) => {
    try {
      const updatedTask = await TaskService.toggleTaskCompletion(taskId);
      setTasks(tasks.map((task) => (task.id === taskId ? updatedTask : task)));
    } catch (error) {
      console.error("Error toggling task completion:", error);
      // In a real app, you'd show an error message to the user
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    try {
      await TaskService.deleteTask(taskId);
      setTasks(tasks.filter((task) => task.id !== taskId));
    } catch (error) {
      console.error("Error deleting task:", error);
      // In a real app, you'd show an error message to the user
    }
  };

  const handleUpdateTask = async (taskId: number, updateData: TaskUpdate) => {
    try {
      const updatedTask = await TaskService.updateTask(taskId, updateData);
      setTasks(tasks.map((task) => (task.id === taskId ? updatedTask : task)));
    } catch (error) {
      console.error("Error updating task:", error);
      // In a real app, you'd show an error message to the user
    }
  };

  if (isLoading || loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-gray-600">Loading tasks...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Redirect is handled by layout
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          My Tasks
        </h1>
        <p className="text-gray-600">
          Manage your tasks below.
        </p>
      </div>

      <div className="mb-6">
        <button
          onClick={() => setShowForm(!showForm)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          {showForm ? "Cancel" : "Create New Task"}
        </button>
      </div>

      {showForm && user && (
        <div className="mb-6">
          <TaskForm
            onSubmit={handleCreateTask}
            onCancel={() => setShowForm(false)}
            userId={user.id}
          />
        </div>
      )}

      <div>
        <h2 className="text-xl font-semibold text-gray-800 mb-4">All Tasks</h2>
        <TaskList
          tasks={tasks}
          onToggleCompletion={handleToggleCompletion}
          onDelete={handleDeleteTask}
          onUpdate={handleUpdateTask}
          loading={loading}
        />
      </div>
    </div>
  );
};

export default TasksPage;