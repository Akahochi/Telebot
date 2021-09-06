import os

# from dotenv import load_dotenv
from telebot import TeleBot

# load_dotenv()

API_TOKEN = API_TOKEN="1986978198:AAES1PbSQxTlqQ960liCvRZVcZwqK1mBrc0"
# API_TOKEN = os.getenv("API_TOKEN")

bot = TeleBot(API_TOKEN)