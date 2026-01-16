"""
Shared in-memory storage for ingestion tasks.
In a real production app, this would be Redis or a database.
"""

# Global dictionaries
tasks: dict[str, dict] = {}
batches: dict[str, dict] = {}

def get_task(task_id: str) -> dict:
    return tasks.get(task_id)

def add_task(task_id: str, data: dict):
    tasks[task_id] = data

def update_task(task_id: str, updates: dict):
    if task_id in tasks:
        tasks[task_id].update(updates)

def get_all_tasks() -> list[dict]:
    return list(tasks.values())
