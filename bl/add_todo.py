import csv
import datetime
import os
import sqlite3

import telebot
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

from bl.constants import users, users_todo, DATA_FORMAT, todos_fildnames
from bl.registration import render_yes_now_keyboard, render_initial_keyboard
from bot import bot
from datetime import datetime

# """
# Таблица SQLite для данных todo
# """
# conn = sqlite3.connect('todo.db', check_same_thread=False)
# cur = conn.cursor()
# cur.execute(
#     """
#     CREATE TABLE IF NOT EXISTS todo(
#     id_db INTEGER PRIMATY KEY,
#     user_id INT NOT NULL,
#     date INT NOT NULL,
#     todo TEXT);
#     """
# )
# conn.commit()


"""
SQLAlchemy table for todo data
"""
engine = create_engine("sqlite+pysqlite:///sqlalchemy_todo.db", echo=True, future=True)
Session = sessionmaker(engine)
Base = declarative_base()


class Todo_text(Base):
    __tablename__ = "todo_text"

    id_db = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    date = Column(String(64), nullable=False)
    todo_text = Column(String(500), nullable=False)

    def __str__(self):
        return f"date:{self.id_db}, " \
               f"user_id:{self.user_id}, " \
               f"date:{self.date}, " \
               f"todo_text:{self.todo_text},"

Base.metadata.create_all(engine)


def is_valid_name_surname(name_surname):
    return not (" " in name_surname or len(name_surname) < 2)


def process_add_todo (user_id, message):
    users_todo[user_id] = {}
    bot.send_message(user_id, 'Enter what you want to do and I will remember')
    bot.register_next_step_handler(message, get_todo)


def get_todo(message):
    user_id = message.from_user.id
    users_todo[user_id]['todo'] = message.text
    bot.send_message(user_id, "Enter the date it is scheduled (dd.mm.yyyy)")
    bot.register_next_step_handler(message, get_data)


def get_data(message):
    user_id = message.from_user.id
    try:
        res = datetime.strptime(message.text, DATA_FORMAT)
    except ValueError:
        bot.send_message(user_id, "Please enter the correct date")
        bot.register_next_step_handler(message, get_data)
    else:
        now = datetime.utcnow()
        if now > res:
            bot.send_message(user_id, "Enter a date in the future")
            bot.register_next_step_handler(message, get_data)
        else:
            users_todo[user_id]["data"] = message.text
            todo = users_todo[user_id]['todo']
            question = f"You planted \n {todo} \n on {message.text} \n Right?"
            render_yes_now_keyboard(user_id, question, "reg2")


"""
Function with writing data to SQAlchemy database
"""

@bot.callback_query_handler(func=lambda call: call.data.startswith("reg2_"))
def callback_worker(call):
    user_id = call.from_user.id
    user_f = {}
    user_f["user_id"] = user_id
    user_f["data"] = users_todo[user_id]["data"]
    user_f["todo"] = users_todo[user_id]['todo']
    if call.data == "reg2_yes":
        bot.send_message(user_id, "Thank you, I will remember!")
        session = Session()
        new_todo = Todo_text(user_id=user_f["user_id"], date=user_f["data"], todo_text=user_f["todo"])
        session.add(new_todo)
        session.flush()
        session.commit()
        session.close()
    elif call.data == "reg2_no":
        users.pop(user_id, None)
        render_initial_keyboard(user_id)


# """
# Function with writing data to SQLite database
# """
#
# @bot.callback_query_handler(func=lambda call: call.data.startswith("reg2_"))
# def callback_worker(call):
#     user_id = call.from_user.id
#     user_f = {}
#     user_f["user_id"] = user_id
#     user_f["data"] = users_todo[user_id]["data"]
#     user_f["todo"] = users_todo[user_id]['todo']
#
#     if call.data == "reg2_yes":
#         bot.send_message(user_id, "Thank you, I will remember!")
#         cur.execute("""
#                 INSERT INTO todo (user_id, date, todo)
#                 VALUES (:user_id, :data, :todo)""", user_f)
#         conn.commit()
#     elif call.data == "reg2_no":
#         users.pop(user_id, None)
#         render_initial_keyboard(user_id)
#
# """
# Function with writing data to CSV
# """

# @bot.callback_query_handler(func=lambda call: call.data.startswith("reg2_"))
# def callback_worker(call):
#     user_id = call.from_user.id
#     user_f = {}
#     user_f["user_id"] = user_id
#     user_f["data"] = users_todo[user_id]["data"]
#     user_f["todo"] = users_todo[user_id]['todo']
#     if call.data == "reg2_yes":
#         bot.send_message(user_id, "Thank you, I will remember!")
#         csv_dir = os.path.join("database")
#         file_path = os.path.join(csv_dir, "users_todo_list.csv")
#         if not os.path.exists(csv_dir):
#             os.makedirs(csv_dir)
#         is_first_todo = not os.path.exists(file_path)
#         with open(file_path, "a") as csv_file:
#             writer = csv.DictWriter(csv_file, fieldnames=todos_fildnames)
#             if is_first_todo:
#                writer.writeheader()
#             writer.writerow(user_f)
#     elif call.data == "reg2_no":
#         users.pop(user_id, None)
#         render_initial_keyboard(user_id)





