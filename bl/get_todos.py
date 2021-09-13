import csv
from datetime import datetime
import os
import sqlite3

from sqlalchemy import and_

from bl.add_todo import Todo_text, Session
from bl.constants import todos_fildnames
from bot import bot


def process_get_todays_todos(user_id):
    # """ For CSV"""
    # file_path = os.path.join("database", "users_todo_list.csv")
    # if not os.path.exists(file_path):
    #     bot.send_message(user_id, "There are no tasks for you today")
    # else:
    #     todos = get_todays_todos(user_id)
    #     bot.send_message(user_id, todos)
    """ For SQLite and For SQAlchemy"""
    todos = get_todays_todos(user_id)
    bot.send_message(user_id, todos)


"""
Function that "pulls" todo from SQAlchemy data
"""


def get_todays_todos(user_id):
    message = ""
    today = datetime.utcnow().date().strftime("%d.%m.%Y")
    with Session() as session:
        some_todo = session.query(Todo_text).filter(and_(Todo_text.date == today, Todo_text.user_id == user_id)).all()
        if not some_todo:
            message = "There are no tasks for you today"
        else:
            f = []
            for row in some_todo:
                f.append(row.todo_text)
            message = f"Hello, your tasks for today: \n {f}"
    return message
    session.commit()


# """
# Function that "pulls" todo from SQLite data
# """
# def get_todays_todos(user_id):
#     conn = sqlite3.connect('todo.db', check_same_thread=False)
#     cur = conn.cursor()
#     message = ""
#     today = datetime.utcnow().date().strftime("%d.%m.%Y")
#     command = """
#             SELECT todo FROM todo
#             WHERE date = ?
#             AND user_id = ?;
#             """
#     result = cur.execute(command, (today, user_id)).fetchall()
#     greeting = "Hello, your tasks for today: \n"
#     message = f"{greeting}{result}"
#     return message


# """
# Function that "pulls" todo from CSV
# """
# def get_todays_todos(user_id):
#     message = ""
#     users_todos = []
#     today = datetime.utcnow().date()
#     csv_dir = os.path.join("database")
#     file_path = os.path.join(csv_dir, "users_todo_list.csv")
#     with open(file_path) as todos_file:
#         reader = csv.DictReader(todos_file, fieldnames=todos_fildnames)
#         for row in reader:
#             if not row["user_id"] == str(user_id):
#                 continue
#             todo_date = datetime.strptime(row["data"], "%d.%m.%Y").date()
#             if todo_date == today:
#                 users_todos.append(row["todo"])
#     if not users_todos:
#         message = "There are no tasks for you today"
#     else:
#         enumerated_todos = []
#         for index, todo in enumerate(users_todos, start=1):
#             enumerated_todos.append(f"{index}, {todo}:")
#         greeting = "Hello, your tasks for today: \n"
#         todos = "\n".join(enumerated_todos)
#         message = f"{greeting}{todos}"
#     return message
