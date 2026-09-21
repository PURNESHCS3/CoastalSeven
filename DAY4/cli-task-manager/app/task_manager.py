from app.database import get_connection
from app.task import Task


class TaskManager:
    """Handles task operations and PostgreSQL persistence."""

    def add_task(self, task):
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                query = """
                    INSERT INTO tasks (title, description, priority)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(
                    query,
                    (task.title, task.description, task.priority),
                )
            connection.commit()
            print("Task added successfully!")
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def view_tasks(self):
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT id, title, description, status, priority, created_at
                    FROM tasks
                    ORDER BY id
                """
                cursor.execute(query)
                rows = cursor.fetchall()

            if not rows:
                print("No tasks found.")
                return

            print("\n========== TASKS ==========")
            for row in rows:
                task = Task(
                    task_id=row[0],
                    title=row[1],
                    description=row[2],
                    status=row[3],
                    priority=row[4],
                    created_at=row[5],
                )
                print("--------------------------------")
                print(task)
        finally:
            connection.close()

    def update_task(self, task_id, new_title, new_description):
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                query = """
                    UPDATE tasks
                    SET title = %s, description = %s
                    WHERE id = %s
                """
                cursor.execute(
                    query,
                    (new_title, new_description, task_id),
                )
                updated = cursor.rowcount
            connection.commit()

            if updated == 0:
                print("Task not found.")
            else:
                print("Task updated successfully!")
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def delete_task(self, task_id):
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM tasks WHERE id = %s",
                    (task_id,),
                )
                deleted = cursor.rowcount
            connection.commit()

            if deleted == 0:
                print("Task not found.")
            else:
                print("Task deleted successfully!")
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def complete_task(self, task_id):
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE tasks SET status = TRUE WHERE id = %s",
                    (task_id,),
                )
                updated = cursor.rowcount
            connection.commit()

            if updated == 0:
                print("Task not found.")
            else:
                print("Task marked as completed!")
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
