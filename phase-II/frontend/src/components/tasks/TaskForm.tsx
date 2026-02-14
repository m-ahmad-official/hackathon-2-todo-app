import React, { useState } from 'react';
import { TaskCreate } from '../../models/task';

interface TaskFormProps {
  onSubmit: (taskData: TaskCreate) => void;
  onCancel: () => void;
  userId: string;
}

const TaskForm: React.FC<TaskFormProps> = ({ onSubmit, onCancel, userId }) => {
  const [formData, setFormData] = useState<Omit<TaskCreate, 'user_id'>>({
    title: '',
    description: '',
    completed: false
  });
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate title
    if (!formData.title.trim()) {
      setError('Title is required');
      return;
    }

    // Submit the task with the user_id
    onSubmit({ ...formData, user_id: userId });
  };

  return (
    <div className="bg-white shadow rounded-lg p-4 mb-4 border border-gray-200">
      <form onSubmit={handleSubmit}>
        {error && (
          <div className="mb-3 p-2 bg-red-100 text-red-700 rounded-md">
            {error}
          </div>
        )}
        <div className="mb-3">
          <label
            htmlFor="title"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Title *
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            className="shadow-sm text-gray-700 focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
            placeholder="Task title"
          />
        </div>
        <div className="mb-3">
          <label
            htmlFor="description"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Description
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description || ""}
            onChange={handleChange}
            rows={3}
            className="shadow-sm text-gray-700 focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
            placeholder="Task description (optional)"
          />
        </div>
        <div className="flex items-center justify-between pt-2">
          <div className="flex items-center">
            <input
              id="completed"
              name="completed"
              type="checkbox"
              checked={formData.completed}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  completed: e.target.checked,
                }))
              }
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label
              htmlFor="completed"
              className="ml-2 block text-sm text-gray-900"
            >
              Completed
            </label>
          </div>
          <div className="space-x-2">
            <button
              type="button"
              onClick={onCancel}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Add Task
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default TaskForm;