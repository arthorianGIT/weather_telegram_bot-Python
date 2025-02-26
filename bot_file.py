import telebot
import requests
from dotenv import load_dotenv
import os

load_dotenv('.env')
api_key = os.getenv('my_api_key')
bot_key = os.getenv('bot_key')

bot = telebot.TeleBot(bot_key)

params = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Hello, you can use me as weather!\n<b>Enter city you want to see</b>', parse_mode='html')
    bot.register_next_step_handler(message, show_weather)

def show_weather(message):
    city = message.text
    global params

    params['q'] = f'{city}'
    params['appid'] = api_key

    response = requests.get('https://api.openweathermap.org/data/2.5/weather', params=params)

    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['description']
        temp = data['main']['temp']

        bot.send_message(message.chat.id, f'<b>Weather description:</b> {weather}\n<b>Temperature:</b> {temp - 273.15:.2f}', parse_mode='html')
    else:
        bot.reply_to(message, f'Error in response: code {response.status_code}\nPlease try again!')


bot.infinity_polling()