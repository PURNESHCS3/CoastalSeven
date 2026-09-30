from app.task import Task
from app.task_manager import TaskManager


def show_menu():
    print("\n========== TASK MANAGER ==========")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Mark Task Complete")
    print("6. Exit")


def add_task(manager):
    title = input("Enter task title: ").strip()
    description = input("Enter task description: ").strip()
    priority = input("Enter priority (Low/Medium/High): ").strip().capitalize()

    if not title:
        print("Task title cannot be empty.")
        return

    if priority not in {"Low", "Medium", "High"}:
        print("Invalid priority. Using Medium.")
        priority = "Medium"

    task = Task(title, description, priority)
    manager.add_task(task)


def run():
    manager = TaskManager()

    while True:
        show_menu()
        choice = input("Enter your choice: ").strip()

        try:
            if choice == "1":
                add_task(manager)

            elif choice == "2":
                manager.view_tasks()

            elif choice == "3":
                task_id = input("Enter task ID: ").strip()
                new_title = input("Enter new title: ").strip()
                new_description = input("Enter new description: ").strip()

                if not new_title:
                    print("Task title cannot be empty.")
                    continue

                manager.update_task(task_id, new_title, new_description)

            elif choice == "4":
                task_id = input("Enter task ID to delete: ").strip()
                manager.delete_task(task_id)

            elif choice == "5":
                task_id = input("Enter task ID: ").strip()
                manager.complete_task(task_id)

            elif choice == "6":
                print("Goodbye!")
                break

            else:
                print("Invalid choice.")

        except Exception as error:
            print(f"An error occurred: {error}")


if __name__ == "__main__":
    run()
