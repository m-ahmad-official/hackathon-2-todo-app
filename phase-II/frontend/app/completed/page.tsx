"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "@/src/providers/AuthProvider";
import TaskList from "@/src/components/tasks/TaskList";
import TaskService from "@/src/services/task-service";
import { TaskResponse, TaskUpdate } from "@/src/models/task";

const CompletedTasksPage: React.FC = () => {
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const { user, isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      // Redirect would be handled by layout
      return;
    }

    if (isAuthenticated && user) {
      loadCompletedTasks();
    }
  }, [isAuthenticated, isLoading, user]);

  const loadCompletedTasks = async () => {
    if (!user) return;

    try {
      setLoading(true);
      // Get all tasks for the authenticated user and filter completed ones
      const userTasks = await TaskService.getTasksByUserId(user.id);
      const completedTasks = userTasks.filter(task => task.completed);
      setTasks(completedTasks);
    } catch (error) {
      console.error("Error loading completed tasks:", error);
      // In a real app, you'd show an error message to the user
    } finally {
      setLoading(false);
    }
  };

  const handleToggleCompletion = async (taskId: number) => {
    try {
      const updatedTask = await TaskService.toggleTaskCompletion(taskId);
      // Update the task in the list
      setTasks(tasks.map((task) => (task.id === taskId ? updatedTask : task)));

      // If the task is now incomplete, remove it from the completed list
      if (!updatedTask.completed) {
        setTasks(tasks.filter((task) => task.id !== taskId));
      }
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
        <p className="text-gray-600">Loading completed tasks...</p>
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
          Completed Tasks
        </h1>
        <p className="text-gray-600">
          View your completed tasks.
        </p>
      </div>

      <div>
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          Completed ({tasks.length})
        </h2>
        <TaskList
          tasks={tasks}
          onToggleCompletion={handleToggleCompletion}
          onDelete={handleDeleteTask}
          onUpdate={handleUpdateTask}
          loading={loading}
          showOnlyCompleted={true}
        />
      </div>
    </div>
  );
};

export default CompletedTasksPage;