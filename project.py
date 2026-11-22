import requests 
import telebot
TOKEN = '8847866237:AAGS5opnB4qTnBDOD9na4prtjcc51q62koY' 
bot = telebot.TeleBot(TOKEN)

def get_random_dog_url(): 
    url1 = 'https://dog.ceo'  
    res = requests.get(url1) 
    data = res.json() 
    return data['message']

@bot.message_handler(commands=['start']) 
def send_welcome(message): 
    bot.send_message(message.chat.id, 'Привет! Напиши /dog или /duck, чтобы получить фото собаки!')
@bot.message_handler(commands=['duck', 'dog']) 
def send_dog_photo(message): 
    try: 
        photo_url = get_random_dog_url()  
        bot.send_photo(message.chat.id, photo_url) 
    except Exception as e: 
        bot.send_message(message.chat.id, "Ой, не удалось получить картинку. Попробуй еще раз!") 
        print(f"Ошибка при получении фото: {e}")
if __name__ == 'main': 
    print('Бот успешно запущен и слушает команды...') 
    bot.infinity_polling(none_stop=True)