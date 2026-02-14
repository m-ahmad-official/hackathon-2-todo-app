import sys
from todo_service import TodoService


def print_menu():
    print("\n--- TODO APP MENU ---")
    print("1. Add Task")
    print("2. View Task List")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Mark Task Complete/Incomplete")
    print("6. Exit")


def add_task_flow(service: TodoService):
    title = input("Enter task title: ")
    try:
        task = service.add_task(title)
        print(f"Success: Task '{task.title}' added with ID {task.id}.")
    except ValueError as e:
        print(f"Error: {e}")


def view_tasks_flow(service: TodoService):
    tasks = service.get_all_tasks()
    if not tasks:
        print("Task list is empty.")
        return

    print("\n--- TASK LIST ---")
    for task in tasks:
        status = "[X]" if task.is_completed else "[ ]"
        print(f"{task.id}. {status} {task.title}")


def update_task_flow(service: TodoService):
    try:
        task_id = int(input("Enter task ID to update: "))
        new_title = input("Enter new title: ")
        if service.update_task(task_id, new_title):
            print("Success: Task updated.")
        else:
            print("Error: Task ID not found.")
    except ValueError:
        print("Error: Please enter a valid numerical ID.")


def delete_task_flow(service: TodoService):
    try:
        task_id = int(input("Enter task ID to delete: "))
        if service.delete_task(task_id):
            print("Success: Task deleted.")
        else:
            print("Error: Task ID not found.")
    except ValueError:
        print("Error: Please enter a valid numerical ID.")


def toggle_task_flow(service: TodoService):
    try:
        task_id = int(input("Enter task ID to toggle: "))
        if service.toggle_completion(task_id):
            print("Success: Task status toggled.")
        else:
            print("Error: Task ID not found.")
    except ValueError:
        print("Error: Please enter a valid numerical ID.")


def main():
    service = TodoService()
    while True:
        print_menu()
        choice = input("Select an option (1-6): ")

        if choice == "1":
            add_task_flow(service)
        elif choice == "2":
            view_tasks_flow(service)
        elif choice == "3":
            update_task_flow(service)
        elif choice == "4":
            delete_task_flow(service)
        elif choice == "5":
            toggle_task_flow(service)
        elif choice == "6":
            print("Exiting application. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid selection. Please choose 1-6.")


if __name__ == "__main__":
    main()
