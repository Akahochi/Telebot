import csv
import datetime
import os

import telebot

from bl.constants import users, users_todo, DATA_FORMAT, todos_fildnames
from bot import bot
from datetime import datetime


def is_valid_name_surname(name_surname):
    return not (" " in name_surname or len(name_surname) < 2)


def process_add_todo (user_id, message):

    users_todo[user_id] = {}
    bot.send_message(user_id, "Введите что вы хотите сделать и я запомню")
    bot.register_next_step_handler(message, get_todo)


def get_todo(message):
    user_id = message.from_user.id
    users_todo[user_id]['todo'] = message.text
    bot.send_message(user_id, "Введите дату, когда это запланировано (дд. мм. гггг)")
    bot.register_next_step_handler(message, get_data)


def get_data(message):
    user_id = message.from_user.id
    try:
        res = datetime.strptime(message.text, DATA_FORMAT)
    except ValueError:
        bot.send_message(user_id, "Введите корректную дату")
        bot.register_next_step_handler(message, get_data)
    else:
        now = datetime.utcnow()
        if now > res:
            bot.send_message(user_id, "Введите дату в будущем")
            bot.register_next_step_handler(message, get_data)
        else:
            users_todo[user_id]["data"] = message.text
            todo = users_todo[user_id]['todo']
            question = f"Ты заплонировал \n {todo} \n на {message.text} \n Верно?"
            render_yes_now_keyboard(user_id, question, "reg2")


@bot.callback_query_handler(func=lambda call: call.data.startswith("reg2_"))
def callback_worker(call):
    user_id = call.from_user.id
    user_f = {}
    user_f["user_id"] = user_id
    user_f["data"] = users_todo[user_id]["data"]
    user_f["todo"] = users_todo[user_id]['todo']
    if call.data == "reg2_yes":
        bot.send_message(user_id, "Спасибо, я запомню!")
        csv_dir = os.path.join("database")
        file_path = os.path.join(csv_dir, "users_todo_list.csv")
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
        is_first_todo = not os.path.exists(file_path)
        with open(file_path, "a") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=todos_fildnames)
            if is_first_todo:
               writer.writeheader()
            writer.writerow(user_f)
    elif call.data == "reg2_no":
        users.pop(user_id, None)
        render_initial_keyboard(user_id)


def render_yes_now_keyboard(user_id: int, question: str, prefix: str):
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_yes = telebot.types.InlineKeyboardButton(text="Да", callback_data=f"{prefix}_yes")
    keyboard.add(key_yes)
    key_no = telebot.types.InlineKeyboardButton(text="Нет", callback_data=f"{prefix}_no")
    keyboard.add(key_no)
    bot.send_message(user_id, text=question, reply_markup=keyboard)


def remove_initial_keyboard(user_id: int, message: str):
    keyboard = telebot.types.ReplyKeyboardRemove()
    bot.send_message(user_id, message, reply_markup=keyboard)


def render_initial_keyboard(user_id: int):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True, one_time_keyboard=True)
    register_button = telebot.types.KeyboardButton("Регистрация")
    login_button = telebot.types.KeyboardButton("TO-DO лист")
    today_todos = telebot.types.KeyboardButton("Что у меня сегодня?")
    keyboard.add(register_button, login_button, today_todos)
    bot.send_message(user_id, "Выберите действие", reply_markup=keyboard)
