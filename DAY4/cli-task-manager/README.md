# CLI Task Manager

A command-line Task Manager built with Python, PostgreSQL, and `psycopg2`.

## Features

- Add tasks
- View tasks
- Update tasks
- Delete tasks
- Mark tasks as completed
- PostgreSQL persistence
- Object-oriented design with `Task` and `TaskManager`
- Environment-based database configuration
- Unit tests using `unittest`

## Project Structure

```text
cli-task-manager/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── task.py
│   ├── task_manager.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   └── test_task.py
├── exports/
├── logs/
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

1. Create the PostgreSQL database and `tasks` table.
2. Update `.env` with your PostgreSQL password.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the application from the project root:

```bash
python -m app.main
```

5. Run tests:

```bash
python -m unittest discover -s tests -v
```

## Security

The `.env` file contains local database credentials and is excluded from Git using `.gitignore`. Never commit real passwords to GitHub.
