from telebot import TeleBot
import os,json,random
from random import choice

TOKEN='8600194513:AAEQbDYbvjrZWT8X-i7GkQRPyncSVT-x6Zs'
bot=TeleBot(TOKEN)


try:
    with open('cities.txt','r',encoding='utf-8') as f:
        cities=[word.strip().lower() for word in f.readlines() if word.strip()]
except FileNotFoundError:
    print('Ошибка: файл "cities.txt" не найден в папке со скриптом')
    cities=[]


game= False
used_cities = []
letter=''

@bot.message_handler(commands=['goroda'])
def start_game(message):
    global game
    global letter
    game = True
    used_cities.clear()
    city = choice(cities)
    used_cities.append(city)
    letter = select_letter(city)
    bot.send_message(message.chat.id, text=city)


def select_letter(text):
    i=1
    while text[-1*i] in ('ь','ы','й','ъ') and i < len(text):
        i +=1
    return text[-1*i]

@bot.message_handler(cammands=['save'])
def save(message):
    with open('scores.json','w',encoding='utf-8') as f:
        json.dump(leaderboard,f)
    bot.send_message(message.chat.id,'Прогресс сохранен!')  
    
@bot.message_handler(commands=['leaderboard'])
def show_leaderboard(message):
    if not os.path.exists('scores.json'):
        bot.send_message(message.chat.id,"Таблица лидеров пока пуста! Сыграйте в игру.")
    try:
        with open('scores.json','r',encoding='utf-8') as f:
            leaderboard_data=json.load(f)
    except Exception:
        bot.send_message(message.chat.id,'Не удалось прочитать таблицу лидеров')
        return
    
    if not leaderboard_data:
        bot.send_message(message.chat.id, "В таблице лидеров пока нет записей")
        return
    sorted_leaders=sorted(leaderboard_data.items(),key=lambda item: item[1], reverse=True)
    
    response_text="Таблица лидеров:**\n\n"
    for index, (name,score) in enumerate(sorted_leaders,start=1):
        response_text +=f"{index}. {name} - {score} очк.\n"
    bot.send_message(message.chat.id, response_text, parse_mode="Markdown")


@bot.message_handler(content_types=['text'])
def  game_logic(message):
    global game, letter,leaderboard
    
    if message.text.startswith('/'):
        return
    
    if not game:
        return 
    user_city=message.text.strip().lower()
    if user_city in used_cities:
        bot.send_message(message.chat.id, 'Этот город уже назывался! Выберите другой.') 
        return

    if not user_city.startswith(letter):
        bot.send_message(message.chat.id,f'Город должен начинаться на букву"{letter.upper()}"!')
        return

    if user_city not in cities:
        bot.send_message(message.chat.id,'Такого города нет в моей базе. Попробуйте другой.')
        return

    used_cities.append(user_city)
    user_name=message.from_user.first_name if message.from_user.first_name else 'Игрок'
    leaderboard[user_name]=leaderboard.get(user_name, 0) + 1

    with open('scores.json','w', encoding='utf-8') as f:
        json.dump(leaderboard, f, ensure_ascii=False, indent=4)
        
    letter=select_letter(user_city)
    available_cities=[c for c in cities if c.startswith(letter) and c not in used_cities]
    

    if not available_cities:
        bot.send_message(message.chat.id, f'Я не знаю городов на эту букву"{letter.upper}". Ты победил')
        game= False
        return
    bot_city=random.choice(available_cities)
    used_cities.append(bot_city)
    letter=select_letter(bot_city)
    bot.send_message(message.chat.id,text=bot_city)
    
    

        



bot.infinity_polling()



