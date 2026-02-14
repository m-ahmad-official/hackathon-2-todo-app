import React from "react";
import TaskCard from "./TaskCard";
import { TaskResponse } from "@/src/models/task";
import { TaskUpdate } from "@/src/models/task";

interface TaskListProps {
  tasks: TaskResponse[];
  onToggleCompletion: (taskId: number) => void;
  onDelete: (taskId: number) => void;
  onUpdate: (taskId: number, updateData: TaskUpdate) => void;
  loading?: boolean;
  showOnlyCompleted?: boolean;
}

const TaskList: React.FC<TaskListProps> = ({
  tasks,
  onToggleCompletion,
  onDelete,
  onUpdate,
  loading = false,
  showOnlyCompleted = false,
}) => {
  // Filter tasks if showOnlyCompleted is true
  const filteredTasks = showOnlyCompleted
    ? tasks.filter((task) => task.completed)
    : tasks;

  if (loading) {
    return (
      <div className="bg-white shadow rounded-lg p-4 mb-4 border border-gray-200">
        <p className="text-center text-gray-500">Loading tasks...</p>
      </div>
    );
  }

  if (filteredTasks.length === 0) {
    return (
      <div className="bg-white shadow rounded-lg p-4 mb-4 border border-gray-200">
        <p className="text-center text-gray-500">
          {showOnlyCompleted
            ? "No completed tasks found."
            : "No tasks found. Create your first task!"}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {filteredTasks.map((task) => (
        <TaskCard
          key={task.id}
          task={task}
          onToggleCompletion={onToggleCompletion}
          onDelete={onDelete}
          onUpdate={onUpdate}
        />
      ))}
    </div>
  );
};

export default TaskList;
