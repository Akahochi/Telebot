from bl.add_todo import process_add_todo
from bl.get_todos import process_get_todays_todos

from bl.registration import process_registration, render_initial_keyboard

from bot import bot


def is_valid_name_surname(name_surname):
    return not (" " in name_surname or len(name_surname) < 2)


@bot.message_handler(content_types=["text"])
def start(message):
    user_id = message.from_user.id
    if message.text == "Registration":
        process_registration(user_id, message)
    elif message.text == "TO-DO":
        process_add_todo(user_id, message)
    elif message.text == "What do I have today?":
         process_get_todays_todos(user_id)
    else:
        render_initial_keyboard(user_id)


if __name__ == "__main__":
    bot.polling(none_stop=True)