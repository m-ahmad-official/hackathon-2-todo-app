import React, { useState } from 'react';
import { TaskResponse, TaskUpdate } from '../../models/task';

interface TaskItemProps {
  task: TaskResponse;
  onToggleCompletion: (taskId: number) => void;
  onDelete: (taskId: number) => void;
  onUpdate: (taskId: number, updateData: TaskUpdate) => void;
}

const TaskItem: React.FC<TaskItemProps> = ({ task, onToggleCompletion, onDelete, onUpdate }) => {
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [editTitle, setEditTitle] = useState<string>(task.title);
  const [editDescription, setEditDescription] = useState<string>(task.description || '');

  const handleToggle = () => {
    onToggleCompletion(task.id);
  };

  const handleDelete = () => {
    onDelete(task.id);
  };

  const handleEditClick = () => {
    setIsEditing(true);
  };

  const handleSaveEdit = () => {
    const updateData: TaskUpdate = {
      title: editTitle,
      description: editDescription,
    };

    onUpdate(task.id, updateData);
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    // Reset to original values
    setEditTitle(task.title);
    setEditDescription(task.description || '');
    setIsEditing(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSaveEdit();
    } else if (e.key === 'Escape') {
      handleCancelEdit();
    }
  };

  return (
    <div className="flex flex-col sm:flex-row sm:items-start space-y-2 sm:space-y-0 sm:space-x-3 p-3 border border-gray-200 rounded-lg">
      <div className="flex items-center h-5 sm:mt-1">
        <input
          type="checkbox"
          checked={task.completed}
          onChange={handleToggle}
          className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
        />
      </div>
      <div className="min-w-0 flex-1 w-full">
        {isEditing ? (
          <div className="space-y-2">
            <input
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              className="block w-full rounded-md text-gray-700 border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              autoFocus
            />
            <textarea
              value={editDescription}
              onChange={(e) => setEditDescription(e.target.value)}
              rows={2}
              className="block w-full rounded-md text-gray-700 border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            />
            <div className="flex flex-wrap gap-2 mt-2">
              <button
                onClick={handleSaveEdit}
                className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                Save
              </button>
              <button
                onClick={handleCancelEdit}
                className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <>
            <p
              className={`text-sm font-medium ${task.completed ? "line-through text-gray-500" : "text-gray-900"}`}
            >
              {task.title}
            </p>
            {task.description && (
              <p
                className={`text-sm ${task.completed ? "text-gray-400" : "text-gray-500"}`}
              >
                {task.description}
              </p>
            )}
            <div className="mt-1 flex flex-wrap items-center text-xs text-gray-500">
              <span>
                Created: {new Date(task.created_at).toLocaleDateString()}
              </span>
              {task.updated_at !== task.created_at && (
                <span className="ml-2">
                  Updated: {new Date(task.updated_at).toLocaleDateString()}
                </span>
              )}
            </div>
          </>
        )}
      </div>
      <div className="flex-shrink-0 flex justify-end w-full sm:w-auto">
        {!isEditing && (
          <div className="flex space-x-1 justify-end">
            <button
              onClick={handleEditClick}
              className="inline-flex items-center p-1 border border-transparent rounded-full text-blue-500 hover:text-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              aria-label="Edit task"
            >
              <svg
                className="h-5 w-5"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
              </svg>
            </button>
            <button
              onClick={handleDelete}
              className="inline-flex items-center p-1 border border-transparent rounded-full text-red-500 hover:text-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              aria-label="Delete task"
            >
              <svg
                className="h-5 w-5"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default TaskItem;