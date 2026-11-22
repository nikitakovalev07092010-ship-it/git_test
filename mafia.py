import threading
from time import sleep
import db
from telebot import TeleBot

TOKEN=('8650934813:AAFMEm3rdG9Ji7eGwvrYhgruy48qbTH-t3I')
bot=TeleBot(TOKEN)

game=False
night=False

def get_killed(night):
    if not night:
        username_killed=db.citizen_kill()
        return f'Горожане выгнали: { username_killed}'
    username_killed=db.mafia_kill()
    return f'Мафия убила: {username_killed}'

def game_loop(message):
    global night,game
    bot.send_message(message.chat.id,'Добро пожаловать в игру! Вам дается 1 минута, чтобы познакомиться')
    sleep(60)
    
    while True:
        if not night:
            bot.send_message(message.chat.id, get_killed(night))
            bot.send_message(message.chat.id, 'Город засыпает, просыпаеться мафия. Наступила ночь')
        else:
            bot.send_message(message.chat.id, get_killed(night))
            bot.send_message(message.chat.id,'Город просыпаеться. Наступил день')
            
        winner=db.check_winner()
        if winner:
            game=False
            bot.send_message(message.chat.id, text=f'Игра окончена! Победили: {winner}')
            return
        
        db.clear(dead=False)
        night=not night
        
        alive=db.get_all_alive()
        alive='\n'.join(alive)
        bot.send_message(message.chat.id,text=f'В игре:\n{alive}')
        
        sleep(60)
        

@bot.message_handler(commands=["start_game"])
def start_game_logic(message):
    global game,night
    
    players_count=db.players_amount()
    
    if players_count < 3:      
        bot.send_message(message.chat.id,"Недостатосно игроков для начала! Нужно хотя бы 3 человека.")
        return
    
    game= True
    night=False
    
    db.clear(dead=True)
    db.set_roles(players_count)
    
    for player_id, role in db.get_player_ids_and_roles():
        bot.send_message(player_id,f'Твоя роль в игре: {role}')
    
    bot.send_message(message.chat.id,"Игра началась! Роли успешно распределены среди участников.")
    
    threading.Thread(target=game_loop,args=(message,)).start()
    

@bot.message_handler(commands=['start'])
def start_game(message):
    player_id=message.from_user.id
    username=message.from_user.username if message.from_user.username else "NoName"
    
    db.insert_player(player_id, username)
    bot.send_message(message.chat.id,f"Привет, {username}! Ты успешно занесен в базу данныx игры.")
    
@bot.message_handler(commands=['count'])
def check_amount(message):
    amount=db.players_amount()
    bot.send_message(message.chat.id,f"Всего игроков в базе данных: {amount}")
    

    
@bot.message_handler(commands=['check'])
def check_database(message):
    count=db.players_amount()
    if count == 0:
        bot.send_message(message.chat.id, "База данных пустая")
        return
    db.set_roles(count)
    
    players_data=db.get_player_ids_and_roles()
    mafia_users=db.get_mafia_usernames()
    report=f"~~Проверка БД~~\n\n"
    report +=f"Игроков в БД:{count}\n"
    report +=f"Список(ID, Роль):{players_data}\n"
    report +=f"Имена мафии:{mafia_users}\n"
    
    bot.send_message(message.chat.id, report, parse_mode="Markdown")
    
@bot.message_handler(commands=['vote'])
def handle_vote_command(message):
    global game,night
    
    if not game:
        bot.reply_to(message, "Игра еще не началась!")
        return
    
    player_id=message.from_user.id
    
    args=message.text.split()
    
    if len(args)<2:
        bot.reply_to(message,"Напиши имя игрока! Пример: /vote @username")
        return
    
    target_username=args[1].replace("@", "")
    
    vote_type="mafia_vote" if night else "citizen_vote"
    
    success=db.vote(vote_type,target_username, player_id)
    
    if success:
        bot.reply_to(message,f"Твой голос против @{target_username} принят.")
    else:
        bot.reply_to(message,"Ошибка! Ты не можешь голосовать (возможно, ты мертв или уже голосовал).")
        

if __name__ == '__main__':   
    bot.infinity_polling()  

