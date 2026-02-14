import React from "react";
import TaskItem from "./TaskItem";
import { TaskResponse, TaskUpdate } from "../../models/task";

interface TaskCardProps {
  task: TaskResponse;
  onToggleCompletion: (taskId: number) => void;
  onDelete: (taskId: number) => void;
  onUpdate: (taskId: number, updateData: TaskUpdate) => void;
}

const TaskCard: React.FC<TaskCardProps> = ({
  task,
  onToggleCompletion,
  onDelete,
  onUpdate,
}) => {
  return (
    <div className="bg-white shadow rounded-lg p-4 mb-3 border border-gray-200">
      <TaskItem
        task={task}
        onToggleCompletion={onToggleCompletion}
        onDelete={onDelete}
        onUpdate={onUpdate}
      />
    </div>
  );
};

export default TaskCard;
