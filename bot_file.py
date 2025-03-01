import telebot
import requests
from dotenv import load_dotenv
import os
import sqlite3

load_dotenv('.env')
api_key = os.getenv('my_api_key')
bot_key = os.getenv('bot_key')

bot = telebot.TeleBot(bot_key)

params = {}

conn = sqlite3.connect('references.sql')
cur = conn.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS names (ref_id int primary key, name text)')
conn.commit()
cur.close()
conn.close()

user_name = ''

@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    conn = sqlite3.connect('references.sql')
    cur = conn.cursor()

    cur.execute('''INSERT OR REPLACE INTO names (ref_id, name) VALUES ('%s', '%s')''' % (1, name))
    conn.commit()
    cur.close()
    conn.close()
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Show Settings', callback_data='settings'))
    global user_name
    if 'user_name' in globals() and user_name != '':
        bot.send_message(message.chat.id, f'Hello <b>{user_name}</b>, you can use me as weather!', parse_mode='html', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f'Hello <b>{name}</b>, you can use me as weather!', parse_mode='html', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def show_settings(call):
    if call.data == 'settings':
        markup = telebot.types.ReplyKeyboardMarkup()
        markup.add(telebot.types.KeyboardButton('Change name reference'))
        markup.add(telebot.types.KeyboardButton('Get Weather'))
    bot.send_message(call.message.chat.id, 'Settings was opened!', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ['Change name reference', 'Get Weather'])
def on_click(message):
    if message.text.lower().strip() == 'change name reference':
        bot.reply_to(message, 'Okay! How do you want me to call you?')
        bot.register_next_step_handler(message, custom_user_name)
    elif message.text.lower().strip() == 'get weather':
        bot.reply_to(message, 'Okay enter the city you want to see!')
        bot.register_next_step_handler(message, show_weather)

def custom_user_name(message):
    conn = sqlite3.connect('references.sql')
    cur = conn.cursor()

    cur.execute('''INSERT OR REPLACE INTO names (ref_id, name) VALUES ('%s', '%s')''' % (2, message.text))
    conn.commit()
    cur.execute('''SELECT name FROM names WHERE ref_id = ?''', (2,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    global user_name
    user_name = result[0]
    bot.send_message(message.chat.id, f"Okay! I'm gonna call you <b>{user_name}</b> now!", parse_mode='html')

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