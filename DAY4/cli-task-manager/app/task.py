class Task:
    """Represents a task in the task manager."""

    def __init__(
        self,
        title,
        description="",
        priority="Medium",
        task_id=None,
        status=False,
        created_at=None,
    ):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status
        self.created_at = created_at

    def mark_completed(self):
        self.status = True

    def __str__(self):
        status = "Completed" if self.status else "Pending"
        return (
            f"ID: {self.task_id}\n"
            f"Title: {self.title}\n"
            f"Description: {self.description}\n"
            f"Status: {status}\n"
            f"Priority: {self.priority}\n"
            f"Created: {self.created_at}"
        )
