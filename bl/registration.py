import csv
import os

from telebot import types

from bl.constants import users, users_todo
from bot import bot


def is_valid_name_surname(name_surname):
    return not (" " in name_surname or len(name_surname) < 2)

def process_registration (user_id, message):

    users[user_id] = {}
    bot.send_message(user_id, 'What is your name?')
    bot.register_next_step_handler(message, get_name)



def get_name(message):
    user_id = message.from_user.id
    name = message.text.title()
    if is_valid_name_surname(name):
        users[user_id]["name"] = name.title()
        bot.send_message(user_id, "Какая у тебя фамилия?")
        bot.register_next_step_handler(message, get_surname)
    else:
        bot.send_message(user_id, "Введите корректное имя")
        bot.register_next_step_handler(message, get_name)



def get_surname(message):
    surname = message.text
    user_id = message.from_user.id
    if is_valid_name_surname(surname):
        users[user_id]["surname"] = surname.title()
        bot.send_message(user_id, "Сколько тебе лет?")
        bot.register_next_step_handler(message, get_age)
    else:
        bot.send_message(user_id, "Введите корректную фамилию")
        bot.register_next_step_handler(message, get_surname)


@bot.callback_query_handler(func=lambda call: call.data.startswith("reg_"))
def callback_worker(call):
    user_id = call.from_user.id
    user_d = {}
    user_d["user_id"] = user_id
    user_d["name"] = users[user_id]["name"]
    user_d["surname"] = users[user_id]["surname"]
    user_d["age"] = users[user_id]["age"]
    if call.data == "reg_yes":
        bot.send_message(user_id, "Спасибо, я запомню!")
        # pretend that we save in database
        csv_dir = os.path.join("database")
        file_path = os.path.join(csv_dir, "users_data.csv")
        names = ["user_id", "name", "surname", "age"]
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
        is_first_todo = not os.path.exists(file_path)
        with open(file_path, "a") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=names)
            if is_first_todo:
                writer.writeheader()
            writer.writerow(user_d)
        with open(file_path) as f:
            print(f.read())
    elif call.data == "reg_no":
        # remove user
        users_todo.pop(user_id, None)
        render_initial_keyboard(user_id)


def get_age(message):
    age_text = message.text
    user_id = message.from_user.id
    if age_text.isdigit():
        age = int(age_text)
        if not 10 <= age <= 100:
            bot.send_message(user_id, "Введите реальный возраст, пожалуйста")
            bot.register_next_step_handler(message, get_age)
        else:
            users[user_id]["age"] = int(age)
            name = users[user_id]["name"]
            surname = users[user_id]["surname"]
            question = f"Тебе {age} лет и тебя зовут {name} {surname} id {user_id}?"
            render_yes_now_keyboard(user_id, question, "reg")
    else:
        bot.send_message(user_id, "Введите цифрами, пожалуйста")
        bot.register_next_step_handler(message, get_age)


def render_yes_now_keyboard(user_id: int, question: str, prefix: str):
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text="Да", callback_data=f"{prefix}_yes")
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text="Нет", callback_data=f"{prefix}_no")
    keyboard.add(key_no)
    bot.send_message(user_id, text=question, reply_markup=keyboard)


def render_initial_keyboard(user_id: int):
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True, one_time_keyboard=True)
    register_button = types.KeyboardButton("Регистрация")
    login_button = types.KeyboardButton("TO-DO лист")
    today_todos = types.KeyboardButton("Что у меня сегодня?")
    keyboard.add(register_button, login_button, today_todos)
    bot.send_message(user_id, "Выберите действие", reply_markup=keyboard)


def remove_initial_keyboard(user_id: int, message: str):
    keyboard = types.ReplyKeyboardRemove()
    bot.send_message(user_id, message, reply_markup=keyboard)