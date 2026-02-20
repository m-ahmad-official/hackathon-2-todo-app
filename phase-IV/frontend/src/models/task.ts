import { z } from "zod";

// Define Zod schemas for validation
const TaskBaseSchema = z.object({
  title: z
    .string()
    .min(1, "Title is required")
    .max(255, "Title must be 255 characters or less"),
  description: z
    .string()
    .max(1000, "Description must be 1000 characters or less")
    .optional()
    .nullable(),
  completed: z.boolean().default(false),
  user_id: z
    .string()
    .min(1, "User ID is required")
    .max(255, "User ID must be 255 characters or less"),
});

const TaskResponseSchema = TaskBaseSchema.extend({
  id: z.number(),
  created_at: z.string(), // ISO date string
  updated_at: z.string(), // ISO date string
});

const TaskCreateSchema = TaskBaseSchema.extend({
  // Additional fields if needed for creation
});

const TaskUpdateSchema = z.object({
  title: z
    .string()
    .min(1, "Title is required")
    .max(255, "Title must be 255 characters or less")
    .optional(),
  description: z
    .string()
    .max(1000, "Description must be 1000 characters or less")
    .optional()
    .nullable(),
  completed: z.boolean().optional(),
});

// Define TypeScript interfaces based on Zod schemas
export interface TaskBase {
  title: string;
  description?: string | null;
  completed: boolean;
  user_id: string;
}

export interface Task extends TaskBase {
  id: number;
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
}

export type TaskCreate = TaskBase;

export interface TaskUpdate {
  title?: string;
  description?: string | null;
  completed?: boolean;
}

export interface TaskResponse extends TaskBase {
  id: number;
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
}

// Export the schemas for validation
export {
  TaskBaseSchema,
  TaskResponseSchema,
  TaskCreateSchema,
  TaskUpdateSchema,
};

// Default export for convenience
export default TaskResponseSchema;
