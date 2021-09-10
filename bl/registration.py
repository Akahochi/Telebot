import csv
import os
import sqlite3

from telebot import types

from bl.constants import users, users_todo
from bot import bot

from sqlalchemy import create_engine, Column, Integer, String, and_
from sqlalchemy.orm import sessionmaker, declarative_base


# """
# SQLite table for registration data
# """
# conn = sqlite3.connect('registration.db', check_same_thread=False)
# cur = conn.cursor()
# cur.execute(
#     """
#     CREATE TABLE IF NOT EXISTS registration(
#     user_id INTEGER PRIMATY KEY,
#     user_id INT NOT NULL,
#     name TEXT,
#     surname TEXT,
#     age INT);
#     """
# )
# conn.commit()

"""
SQLAlchemy table for registration data
"""
engine = create_engine("sqlite+pysqlite:///sqlalchemy_registration.db", echo=True, future=True)
Session = sessionmaker(engine)
Base = declarative_base()


class Registration(Base):
    __tablename__ = "registration"

    id_db = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String(64), nullable=False)
    surname = Column(String(64), nullable=False)
    age = Column(Integer, nullable=False)

    def __str__(self):
        return f"user_id:{self.user_id}, " \
               f"name:{self.name}, " \
               f"surname:{self.surname}," \
               f"age:{self.age},"


Base.metadata.create_all(engine)



def is_valid_name_surname(name_surname):
    return not (" " in name_surname or len(name_surname) < 2)


def process_registration(user_id, message):
    users[user_id] = {}
    bot.send_message(user_id, 'What is your name?')
    bot.register_next_step_handler(message, get_name)


def get_name(message):
    user_id = message.from_user.id
    name = message.text.title()
    if is_valid_name_surname(name):
        users[user_id]["name"] = name.title()
        bot.send_message(user_id, "What is your last name?")
        bot.register_next_step_handler(message, get_surname)
    else:
        bot.send_message(user_id, "Please enter a valid name")
        bot.register_next_step_handler(message, get_name)


def get_surname(message):
    surname = message.text
    user_id = message.from_user.id
    if is_valid_name_surname(surname):
        users[user_id]["surname"] = surname.title()
        bot.send_message(user_id, "How old are you?")
        bot.register_next_step_handler(message, get_age)
    else:
        bot.send_message(user_id, "Please enter a valid last name")
        bot.register_next_step_handler(message, get_surname)


# """
# Function with writing data to SQLite database
# """
#
#
# @bot.callback_query_handler(func=lambda call: call.data.startswith("reg_"))
# def callback_worker(call):
#     user_id = call.from_user.id
#     user_d = {}
#     user_d["user_id"] = user_id
#     user_d["name"] = users[user_id]["name"]
#     user_d["surname"] = users[user_id]["surname"]
#     user_d["age"] = users[user_id]["age"]
#
#     if call.data == "reg_yes":
#         bot.send_message(user_id, "Thank you, I will remember!")
#         # pretend that we save in database
#         cur.execute("""
#         INSERT INTO registration (user_id, name, surname, age)
#         VALUES (:user_id,:name,:surname,:age)""", user_d)
#         conn.commit()
#     elif call.data == "reg_no":
#         # remove user
#         users_todo.pop(user_id, None)
#         render_initial_keyboard(user_id)


"""
Function with writing data to SQLAlchemy database
"""

@bot.callback_query_handler(func=lambda call: call.data.startswith("reg_"))
def callback_worker(call):
    user_id = call.from_user.id
    user_d = {}
    user_d["user_id"] = user_id
    user_d["name"] = users[user_id]["name"]
    user_d["surname"] = users[user_id]["surname"]
    user_d["age"] = users[user_id]["age"]
    if call.data == "reg_yes":
        bot.send_message(user_id, "Thank you, I will remember!")
        # pretend that we save in database
        session = Session()
        new_user = Registration(user_id=user_d["user_id"], name=user_d["name"], surname=user_d["surname"], age=user_d["age"])
        session.add(new_user)
        session.flush()
        session.commit()
        session.close()
    elif call.data == "reg_no":
        # remove user
        users_todo.pop(user_id, None)
        render_initial_keyboard(user_id)

# """
# Function with writing data to csv
# """
# @bot.callback_query_handler(func=lambda call: call.data.startswith("reg_"))
# def callback_worker(call):
#     user_id = call.from_user.id
#     user_d = {}
#     user_d["user_id"] = user_id
#     user_d["name"] = users[user_id]["name"]
#     user_d["surname"] = users[user_id]["surname"]
#     user_d["age"] = users[user_id]["age"]
#     if call.data == "reg_yes":
#         bot.send_message(user_id, "Thank you, I will remember!")
#         # pretend that we save in database
#         csv_dir = os.path.join("database")
#         file_path = os.path.join(csv_dir, "users_data.csv")
#         names = ["user_id", "name", "surname", "age"]
#         if not os.path.exists(csv_dir):
#             os.makedirs(csv_dir)
#         is_first_todo = not os.path.exists(file_path)
#         with open(file_path, "a") as csv_file:
#             writer = csv.DictWriter(csv_file, fieldnames=names)
#             if is_first_todo:
#                 writer.writeheader()
#             writer.writerow(user_d)
#         with open(file_path) as f:
#             print(f.read())
#     elif call.data == "reg_no":
#         # remove user
#         users_todo.pop(user_id, None)
#         render_initial_keyboard(user_id)


def get_age(message):
    age_text = message.text
    user_id = message.from_user.id
    if age_text.isdigit():
        age = int(age_text)
        if not 10 <= age <= 100:
            bot.send_message(user_id, "Please enter your real age")
            bot.register_next_step_handler(message, get_age)
        else:
            users[user_id]["age"] = int(age)
            name = users[user_id]["name"]
            surname = users[user_id]["surname"]
            question = f"You {age} years old and your name is {name} {surname} id {user_id}?"
            render_yes_now_keyboard(user_id, question, "reg")
    else:
        bot.send_message(user_id, "Enter in numbers, please")
        bot.register_next_step_handler(message, get_age)


def render_yes_now_keyboard(user_id: int, question: str, prefix: str):
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text="Yes", callback_data=f"{prefix}_yes")
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text="No", callback_data=f"{prefix}_no")
    keyboard.add(key_no)
    bot.send_message(user_id, text=question, reply_markup=keyboard)


def render_initial_keyboard(user_id: int):
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True, one_time_keyboard=True)
    register_button = types.KeyboardButton("Registration")
    login_button = types.KeyboardButton("TO-DO")
    today_todos = types.KeyboardButton("What do I have today?")
    keyboard.add(register_button, login_button, today_todos)
    bot.send_message(user_id, "Choose an action", reply_markup=keyboard)


def remove_initial_keyboard(user_id: int, message: str):
    keyboard = types.ReplyKeyboardRemove()
    bot.send_message(user_id, message, reply_markup=keyboard)
