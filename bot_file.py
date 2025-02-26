import telebot
import requests
from dotenv import load_dotenv
import os

load_dotenv('.env')
api_key = os.getenv('my_api_key')
bot_key = os.getenv('bot_key')

bot = telebot.TeleBot(bot_key)