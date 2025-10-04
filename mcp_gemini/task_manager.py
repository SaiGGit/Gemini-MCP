import json
from pathlib import Path

TASKS_FILE = "tasks.json"

def load_tasks():
    if Path(TASKS_FILE).exists():
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

def list_tasks():
    return [t["task"] for t in load_tasks()]

def add_task(task_text):
    tasks = load_tasks()
    if not any(t["task"] == task_text for t in tasks):
        tasks.append({"task": task_text})
        save_tasks(tasks)

def delete_task(task_text):
    tasks = load_tasks()
    new_tasks = [t for t in tasks if t["task"] != task_text]
    if len(new_tasks) != len(tasks):
        save_tasks(new_tasks)

def clear_tasks():
    save_tasks([])
