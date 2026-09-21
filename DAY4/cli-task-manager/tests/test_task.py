import unittest
from app.task import Task


class TestTask(unittest.TestCase):

    def test_task_creation(self):
        task = Task("Learn Python", "Study OOP", "High")

        self.assertEqual(task.title, "Learn Python")
        self.assertEqual(task.description, "Study OOP")
        self.assertEqual(task.priority, "High")
        self.assertFalse(task.status)

    def test_mark_completed(self):
        task = Task("Learn SQL")

        task.mark_completed()

        self.assertTrue(task.status)

    def test_task_string(self):
        task = Task(
            "Learn Git",
            "Practice GitHub Flow",
            "Medium",
            task_id=1,
        )

        result = str(task)

        self.assertIn("Learn Git", result)
        self.assertIn("Pending", result)


if __name__ == "__main__":
    unittest.main()
