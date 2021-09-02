import csv
import datetime
import os

from bl.constants import todos_fildnames
from bot import bot


def process_get_todays_todos(user_id):
    file_path = os.path.join("database", "users_todo_list.csv")
    if not os.path.exists(file_path):
        bot.send_message(user_id, "Для вас нет задач на сегодня")
    else:
        todos = get_todays_todos(user_id)
        bot.send_message(user_id, todos)

def get_todays_todos(user_id):
    message = ""
    users_todos = []
    today = datetime.utcnow().date()
    csv_dir = os.path.join("database")
    file_path = os.path.join(csv_dir, "users_todo_list.csv")
    with open(file_path) as todos_file:
        reader = csv.DictReader(todos_file, fieldnames=todos_fildnames)
        for row in reader:
            if not row["user_id"] == str(user_id):
                continue
            todo_date = datetime.strptime(row["data"], "%d.%m.%Y").date()
            if todo_date == today:
                users_todos.append(row["todo"])
    if not users_todos:
        message = "Для вас нет задач на сегодня"
    else:
        enumerated_todos = []
        for index, todo in enumerate(users_todos, start=1):
            enumerated_todos.append(f"{index}, {todo}:")
        greeting = "Здравствуйте, ваши задачи на сегодня: \n"
        todos = "\n".join(enumerated_todos)
        message = f"{greeting}{todos}"
    return message

