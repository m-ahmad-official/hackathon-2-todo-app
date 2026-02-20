import { TaskCreate, TaskResponse, TaskUpdate } from "../models/task";
import { apiClient } from "./api-client";

class TaskService {
  /**
   * Create a new task
   */
  static async createTask(taskData: TaskCreate): Promise<TaskResponse> {
    try {
      const response = await apiClient.post<TaskResponse>("/tasks/", taskData);
      return response.data;
    } catch (error) {
      console.error("Error creating task:", error);
      throw error;
    }
  }

  /**
   * Get all tasks for a specific user
   */
  static async getTasksByUserId(userId: string): Promise<TaskResponse[]> {
    try {
      const response = await apiClient.get<TaskResponse[]>(
        `/tasks/user/${userId}`,
      );
      return response.data;
    } catch (error) {
      console.error("Error getting tasks for user:", error);
      throw error;
    }
  }

  /**
   * Get a specific task by ID
   */
  static async getTaskById(taskId: number): Promise<TaskResponse | null> {
    try {
      const response = await apiClient.get<TaskResponse>(`/tasks/${taskId}`);
      return response.data;
    } catch (error: unknown) {
      if (
        // Type narrowing
        (error as { response?: { status?: number } })?.response?.status === 404
      ) {
        return null;
      }
      console.error("Error getting task by ID:", error);
      throw error;
    }
  }

  /**
   * Update a task by ID
   */
  static async updateTask(
    taskId: number,
    taskUpdate: TaskUpdate,
  ): Promise<TaskResponse> {
    try {
      const response = await apiClient.put<TaskResponse>(
        `/tasks/${taskId}`,
        taskUpdate,
      );
      return response.data;
    } catch (error) {
      console.error("Error updating task:", error);
      throw error;
    }
  }

  /**
   * Toggle task completion status
   */
  static async toggleTaskCompletion(taskId: number): Promise<TaskResponse> {
    try {
      const response = await apiClient.patch<TaskResponse>(
        `/tasks/${taskId}/toggle`,
      );
      return response.data;
    } catch (error) {
      console.error("Error toggling task completion:", error);
      throw error;
    }
  }

  /**
   * Delete a task by ID
   */
  static async deleteTask(taskId: number): Promise<boolean> {
    try {
      await apiClient.delete(`/tasks/${taskId}`);
      return true;
    } catch (error) {
      console.error("Error deleting task:", error);
      throw error;
    }
  }
}

export default TaskService;
