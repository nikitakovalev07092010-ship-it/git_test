import time
from random import randint
import telebot
from telebot import types


TOKEN='8566966188:AAFPTgdaNGstZ2NFvPIKN8ysSfkwlXdwAlY'
bot=telebot.TeleBot(TOKEN)

sum_check=0


import json
import os
WARNS_FILE='warns.json'

def load_warns():
    if os.path.exists(WARNS_FILE):
        with open(WARNS_FILE,'r', encoding='utf-8') as f: 
            return json.load(f)
    return {}

def save_warns(warns):
    with open(WARNS_FILE,'w', encoding='utf-8') as f:
        return json.load(f)
    return {}

def add_warn(chat_id, user_id, user_name):
    warns=load_warns()
    
    key=f'{chat_id}_{user_id}'
    
    current_warns = warns.get(key, 0) + 1
    warns[key] = current_warns 
    save_warns(warns)
    
    if current_warns >= 3:
        bot.ban_chat_member(chat_id, user_id)
        warns[key] = 0
        save_warns(warns)
        bot.send_message(chat_id,f'Пользователь {user_name} получил 3/3 предупреждений и был забанен!')
    else:
        bot.send_message(chat_id,f'{user_name}, нарушаешь! Получено предупреждение: *{current_warns}/3*\nПосле 3-го предупреждения последует бан.',parse_mode='Markdown')
            
    



def is_group(message):
    return message.chat.type in ('group','supergroup')

try:
    with open('bad_words.txt','r',encoding='utf-8') as f:
        data=[word.strip().lower() for word in f.readlines()]
except FileNotFoundError:
    data = []
    print('файл не был найден')
    
    
def has_bad_words(text):
    message_words=text.split(' ')
    for word in message_words:
        if word in data:
            return True
    return False


@bot.message_handler(func=lambda message: message.entities is not None and is_group(message))
def delete_links(message):
    for entity in message.entities:
        if entity.type in ['url','text_link']:
            bot.delete_message(message.chat.id, message.message_id)
            break

@bot.message_handler(func=lambda message: has_bad_words(message.text.lower()) and is_group(message))
def handle_bad_words(message):
    bot.delete_message(message.chat.id, message.message_id)
    
    user_id=message.from_user.id
    user_name=message.from_user.first_name
    chat_id=message.chat.id
    
    add_warn(chat_id,user_id,user_name)
    
    global sum_check
    n1=randint(1, 5)
    n2=randint(1, 5)
    sum_check=n1 + n2
    
    keyboard=types.InlineKeyboardMarkup()
    numbers=['один','два','три','четыре','пять','шесть','семь','восемь','девять','десять']
    keys=[]
    
    for indx, number in enumerate(numbers):
        keys.append(types.InlineKeyboardButton(text=number, callback_data=str(indx + 1)))
        
    keyboard.row(*keys)
    
    
    bot.send_message(message.chat.id,f'Решите пример: {n1} + {n2} = ?',reply_markup=keyboard)
    
@bot.callback_query_handler(func=lambda call:call.data)
def callback_inline(call):
    global sum_check
    if int(call.data) == sum_check:
        bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text='Проверка пройдена')
        
    if int(call.data) != sum_check:
        bot.ban_chat_member(call.message.chat.id,call.from_user.id)
        
        bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text='Проверка не пройдена. Пользователь заблокирован.')
        
if __name__=='__main__':
    print('++++++++++')
    bot.infinity_polling()