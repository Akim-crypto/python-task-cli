import argparse
import json
import os
from datetime import datetime
from enum import Enum

TASK_FILE = "tasks.json"


class Status(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"

    @classmethod
    def values(cls) -> list[str]:
        return [s.value for s in cls]


def current_time() -> str:
    return datetime.now().isoformat(timespec="seconds")


def load_data() -> dict:
    if not os.path.exists(TASK_FILE):
        return {"last_id": 0, "tasks": []}

    try:
        with open(TASK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Бэкап поврежденного файла
        backup_name = TASK_FILE + ".bak"
        os.replace(TASK_FILE, backup_name)
        print(f"Ошибка: файл {TASK_FILE} поврежден, создан бэкап {backup_name}")
        return {"last_id": 0, "tasks": []}


def save_data(data: dict) -> None:
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def find_task(data: dict, task_id: int) -> dict | None:
    for task in data["tasks"]:
        if task["id"] == task_id:
            return task
    return None


def validate_description(description: str) -> str:
    description = description.strip()
    if not description:
        raise ValueError("Description cannot be empty")
    if len(description) > 255:
        raise ValueError("Description is too long (max 255 chars)")
    return description


def parse_task_id(raw_id: str) -> int:
    try:
        return int(raw_id)
    except ValueError:
        raise ValueError("Task ID must be an integer")


def cmd_add(description: str) -> None:
    description = validate_description(description)

    data = load_data()
    new_id = data["last_id"] + 1
    now = current_time()

    task = {
        "id": new_id,
        "description": description,
        "status": Status.TODO.value,
        "createdAt": now,
        "updatedAt": now,
    }

    data["last_id"] = new_id
    data["tasks"].append(task)
    save_data(data)

    print(f"Task added successfully (ID: {new_id})")


def cmd_update(task_id: int, description: str) -> None:
    description = validate_description(description)

    data = load_data()
    task = find_task(data, task_id)

    if not task:
        print(f"Task with ID {task_id} not found")
        return

    task["description"] = description
    task["updatedAt"] = current_time()
    save_data(data)

    print(f"Task {task_id} updated successfully")


def cmd_delete(task_id: int) -> None:
    data = load_data()
    before = len(data["tasks"])
    data["tasks"] = [t for t in data["tasks"] if t["id"] != task_id]
    after = len(data["tasks"])

    if before == after:
        print(f"Task with ID {task_id} not found")
        return

    save_data(data)
    print(f"Task {task_id} deleted successfully")


def change_status(task_id: int, new_status: str) -> None:
    if new_status not in Status.values():
        print(f"Invalid status '{new_status}'. Valid: {', '.join(Status.values())}")
        return

    data = load_data()
    task = find_task(data, task_id)

    if not task:
        print(f"Task with ID {task_id} not found")
        return

    task["status"] = new_status
    task["updatedAt"] = current_time()
    save_data(data)

    print(f"Task {task_id} marked as {new_status}")


def cmd_mark_todo(task_id: int) -> None:
    change_status(task_id, Status.TODO.value)


def cmd_mark_in_progress(task_id: int) -> None:
    change_status(task_id, Status.IN_PROGRESS.value)


def cmd_mark_done(task_id: int) -> None:
    change_status(task_id, Status.DONE.value)


def print_task(task: dict) -> None:
    print(f"[{task['id']}] ({task['status']}) {task['description']}")
    print(f"  createdAt: {task['createdAt']}")
    print(f"  updatedAt: {task['updatedAt']}")
    print()


def cmd_list(status: str | None = None) -> None:
    data = load_data()
    tasks = data["tasks"]

    if status:
        if status not in Status.values():
            print(f"Invalid status '{status}'. Valid: {', '.join(Status.values())}")
            return
        tasks = [t for t in tasks if t["status"] == status]

    if not tasks:
        if status:
            print(f"No tasks with status '{status}'")
        else:
            print("No tasks found")
        return

    for task in tasks:
        print_task(task)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Task Tracker CLI (Python version)"
    )

    parser.add_argument(
        "command",
        help="Command to run",
        choices=[
            "add",
            "update",
            "delete",
            "mark-todo",
            "mark-in-progress",
            "mark-done",
            "list",
        ],
    )

    # Доп. аргументы, смысл зависит от команды
    parser.add_argument("arg1", nargs="?", help="ID или статус / описание")
    parser.add_argument("arg2", nargs="?", help="Описание (для update)")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    cmd = args.command

    if cmd == "add":
        if not args.arg1:
            parser.error("Description is required for 'add'")
        cmd_add(args.arg1)

    elif cmd == "update":
        if not args.arg1 or not args.arg2:
            parser.error('Usage: update <id> "new description"')
        try:
            task_id = parse_task_id(args.arg1)
        except ValueError as e:
            print(e)
            return
        cmd_update(task_id, args.arg2)

    elif cmd == "delete":
        if not args.arg1:
            parser.error("Usage: delete <id>")
        try:
            task_id = parse_task_id(args.arg1)
        except ValueError as e:
            print(e)
            return
        cmd_delete(task_id)

    elif cmd == "mark-todo":
        if not args.arg1:
            parser.error("Usage: mark-todo <id>")
        try:
            task_id = parse_task_id(args.arg1)
        except ValueError as e:
            print(e)
            return
        cmd_mark_todo(task_id)

    elif cmd == "mark-in-progress":
        if not args.arg1:
            parser.error("Usage: mark-in-progress <id>")
        try:
            task_id = parse_task_id(args.arg1)
        except ValueError as e:
            print(e)
            return
        cmd_mark_in_progress(task_id)

    elif cmd == "mark-done":
        if not args.arg1:
            parser.error("Usage: mark-done <id>")
        try:
            task_id = parse_task_id(args.arg1)
        except ValueError as e:
            print(e)
            return
        cmd_mark_done(task_id)

    elif cmd == "list":
        status = args.arg1 if args.arg1 else None
        cmd_list(status)


if __name__ == "__main__":
    main()
