import telebot
from telebot import types

API_TOKEN = "1871780340:AAFGbec7XrsGd_a_yj62HFSbCZvzkj_7ff4"

bot = telebot.TeleBot(API_TOKEN)

users = {}

users_todo = {}
print(users)


def is_valid_name_surname(name_surname):
    return not (" " in name_surname or len(name_surname) < 2)


@bot.message_handler(content_types=["text"])
def start(message):
    user_id = message.from_user.id
    if message.text == "Регистрация":
        # create empty user
        users[user_id] = {}
        remove_initial_keyboard(user_id, "Как тебя зовут?")
        bot.register_next_step_handler(message, get_name)
    elif message.text == "TO-DO лист":
        users_todo[user_id] = {}
        remove_initial_keyboard(user_id, "Введите что вы хотите сделать и я запомню")
        bot.register_next_step_handler(message, get_todo)
    else:
        render_initial_keyboard(user_id)


def get_todo(message):
    user_id = message.from_user.id
    todo = message.text
    users_todo[user_id]['todo'] = todo
    bot.send_message(user_id, "Введите дату, когда это запланировано (дд. мм. гггг)")
    bot.register_next_step_handler(message, get_data)


from datetime import datetime

def get_data(message):
    user_id = message.from_user.id
    data = message.text
    try:
        res = datetime.strptime(data, "%d.%m.%Y")
        users_todo[user_id]["data"] = data
        todo = users_todo[user_id]['todo']
        question = f"Ты заплонировал {todo} на {data}?"
        render_yes_now_keyboard(user_id, question, "reg2")
    except ValueError:
        bot.send_message(user_id, "Введите корректную дату")
        bot.register_next_step_handler(message, get_data)



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


import csv
import os


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
        csv_dir = os.path.join("test_files1", "csv")
        file_path = os.path.join(csv_dir, "users_data.csv")
        names = ["user_id", "name", "surname", "age"]
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
        with open(file_path, "a") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=names)
            writer.writeheader()
            writer.writerow(user_d)
        with open(file_path) as f:
            print(f.read())
    elif call.data == "reg_no":
        # remove user
        users_todo.pop(user_id, None)
        render_initial_keyboard(user_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("reg2_"))
def callback_worker(call):
    user_id = call.from_user.id
    user_f = {}
    user_f["user_id"] = user_id
    user_f["data"] = users_todo[user_id]["data"]
    user_f["todo"] = users_todo[user_id]['todo']
    if call.data == "reg2_yes":
        bot.send_message(user_id, "Спасибо, я запомню!")
        # pretend that we save in database
        csv_dir = os.path.join("test_files1", "csv")
        file_path = os.path.join(csv_dir, "users_todo_list.csv")
        names2 = ["user_id", "data", "todo"]
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
        with open(file_path, "a") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=names2)
            writer.writeheader()
            writer.writerow(user_f)
        with open(file_path) as c:
            print(c.read())
    elif call.data == "reg2_no":
        # remove user
        users.pop(user_id, None)
        render_initial_keyboard(user_id)


def render_yes_now_keyboard(user_id: int, question: str, prefix: str):
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text="Да", callback_data=f"{prefix}_yes")
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text="Нет", callback_data=f"{prefix}_no")
    keyboard.add(key_no)
    bot.send_message(user_id, text=question, reply_markup=keyboard)


def render_initial_keyboard(user_id: int):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    register_button = types.KeyboardButton("Регистрация")
    login_button = types.KeyboardButton("TO-DO лист")
    keyboard.add(register_button, login_button)
    bot.send_message(user_id, "Выберите действие", reply_markup=keyboard)


def remove_initial_keyboard(user_id: int, message: str):
    keyboard = types.ReplyKeyboardRemove()
    bot.send_message(user_id, message, reply_markup=keyboard)


if __name__ == "__main__":
    bot.polling(none_stop=True)