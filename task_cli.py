import json
import os
import argparse
from datetime import datetime

TASK_FILE = "tasks.json"

VALID_STATUSES = ["todo","in-progress","done"]


def current_time():
    return datetime.now().isoformat(timespec="seconds")

def load_data():
    if os.path.exists(TASK_FILE):
        try:
            with open(TASK_FILE, "r" , encoding="utf-8") as f :
                return json.load(f)
        except json.JSONDecodeError:
            print("Ошибка: файл tasks.json поврежден - создаю новый")
    return {"last_id":0, "tasks":[]}


def save_data(data):
    with open(TASK_FILE , "w" , encoding="utf-8") as f:
        json.dump(data,f,indent=4,ensure_ascii=False)


def find_task(data,task_id):
    for task in data["tasks"]:
        if task["id"] == task_id:
            return task
    return None


def cmd_add(description):
    data = load_data()
    new_id = data["last_id"] + 1 
    now = current_time()

    task = {
        "id": new_id,
        "description": description,
        "status":"todo",
        "createdAt":now,
        "updatedAt":now,
    }

    data["last_id"] = new_id
    data["tasks"].append(task)
    save_data(data)

    print(f"Task added succesfully (ID: {new_id})")


def cmd_update(task_id , description):
    data = load_data()
    task = find_task(data , task_id)
    if not task:
        print(f"Task with ID {task_id} not found")
        return
    
    task["description"] = description
    task["updatedAt"] = current_time()
    save_data(data)
    print(f"Task {task_id} updated successfully")


def cmd_delete(task_id):
    data = load_data()
    before = len(data["tasks"])
    data["tasks"] = [t for t in data["tasks"] if t["id"] != task_id]
    after = len(data["tasks"])

    if before == after:
        print(f"Task with ID {task_id} not found")
        return
    
    save_data(data)
    print(f"Task {task_id} deleted successfully")


def change_status(task_id , new_status):

    if new_status not in VALID_STATUSES:
        print(f"Invalid status '{new_status}'. valid: {', '.join(VALID_STATUSES)}")
        return
    

    data = load_data()
    task = find_task(data , task_id)
    if not task:
        print(f"Task with id {task_id} not found")
        return
    

    task["status"] = new_status
    task["updatedAt"] = current_time()
    save_data(data)
    print(f"Task {task_id} marked as {new_status}")


def cmd_mark_todo(task_id):
    change_status(task_id , "todo")


def cmd_mark_in_progress(task_id):
    change_status(task_id , "in-progress")


def cmd_mark_done(task_id):
    change_status(task_id,"done")


def print_task(task):
    print(f"[{task['id']}] ({task['status']}) {task['description']}")
    print(f"  createdAt: {task['createdAt']}")
    print(f"  updatedAt: {task['updatedAt']}")
    print()



def cmd_list(status=None):
    """
    Вывести список задач.
    - без статуса: все
    - с статусом: только задачи с этим статусом
    """
    data = load_data()
    tasks = data["tasks"]

    if status:
        if status not in VALID_STATUSES:
            print(f"Invalid status '{status}'. Valid: {', '.join(VALID_STATUSES)}")
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


# ====== CLI (argparse) ======


def build_parser():
    parser = argparse.ArgumentParser(
        description="Task Tracker CLI (Python version)"
    )

    parser.add_argument(
        "command",
        help="Command to run",
        choices=[
            "add", "update", "delete",
            "mark-todo", "mark-in-progress", "mark-done",
            "list",
        ],
    )

    # Доп. аргументы, смысл зависит от команды
    parser.add_argument("arg1", nargs="?", help="ID или статус / описание")
    parser.add_argument("arg2", nargs="?", help="Описание (для update)")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    cmd = args.command

    if cmd == "add":
        # add "описание"
        if not args.arg1:
            print("Description is required for 'add'")
            print('Example: python task_cli.py add "Buy groceries"')
            return
        cmd_add(args.arg1)

    elif cmd == "update":
        # update <id> "новое описание"
        if not args.arg1 or not args.arg2:
            print("Usage: update <id> \"new description\"")
            print('Example: python task_cli.py update 1 "New description"')
            return
        try:
            task_id = int(args.arg1)
        except ValueError:
            print("Task ID must be an integer")
            return
        cmd_update(task_id, args.arg2)

    elif cmd == "delete":
        # delete <id>
        if not args.arg1:
            print("Usage: delete <id>")
            return
        try:
            task_id = int(args.arg1)
        except ValueError:
            print("Task ID must be an integer")
            return
        cmd_delete(task_id)

    elif cmd == "mark-todo":
        # mark-todo <id>
        if not args.arg1:
            print("Usage: mark-todo <id>")
            return
        try:
            task_id = int(args.arg1)
        except ValueError:
            print("Task ID must be an integer")
            return
        cmd_mark_todo(task_id)

    elif cmd == "mark-in-progress":
        # mark-in-progress <id>
        if not args.arg1:
            print("Usage: mark-in-progress <id>")
            return
        try:
            task_id = int(args.arg1)
        except ValueError:
            print("Task ID must be an integer")
            return
        cmd_mark_in_progress(task_id)

    elif cmd == "mark-done":
        # mark-done <id>
        if not args.arg1:
            print("Usage: mark-done <id>")
            return
        try:
            task_id = int(args.arg1)
        except ValueError:
            print("Task ID must be an integer")
            return
        cmd_mark_done(task_id)

    elif cmd == "list":
        # list
        # list todo
        # list in-progress
        # list done
        status = args.arg1 if args.arg1 else None
        cmd_list(status)


if __name__ == "__main__":
    main()