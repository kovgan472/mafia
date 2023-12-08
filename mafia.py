from time import*
from telebot import TeleBot
import db


TOKEN = '6410926325:AAFME_4bNOaUbvSqligYnzAW_J78pWNdaTc'
bot = TeleBot(TOKEN)



game = False
night = False

def get_killed(night):
    if not night:
        username_killed = db.citizens_kill()
        return f'Горожане выгнали: {username_killed}'
    username_killed = db.mafia_kill()
    return f'Мафия убила: {username_killed}'

@bot.message_handler(func=lambda m: m.text.lower() == 'готов' and m.chat.type == 'private')
def send_text(message):
    bot.send_message(message.chat.id, f'{message.from_user.first_name} играет') 
    bot.send_message(message.from_user.id, 'Вы добавлены в игру')
    db.insert_player(message.from_user.id, username=message.from_user.first_name)

                        


@bot.message_handler(commands =['game'])
def game_start(message):
    global game
    players = db.player_amount()
    if players >= 5 and not game:
        db.set_rules(players)
        players_roles = db.get_players_role()
        mafia_usernames = db.get_mafia_username()
        for player_id, role in players_roles:
            try:
          
                bot.send_message(player_id, text=role)
                if role == 'mafia':
                    
                    bot.send_message(player_id, text=f'Все члены мафии:\n{mafia_usernames}')
            except:
                pass
        game = True
        bot.send_message(message.chat.id, text = 'Игра началась!')
        return 
    bot.send_message(message.chat.id, text ='недостаточно людей!')




@bot.message_handler(commands=["kick"])
def kick(message):
    username = ' '.join(message.text.split(' ')[1:])
    usernames = db.get_all_alive()
    if not night:
        if not username in usernames:
            bot.send_message(message.chat.id, 'Такого имени нет')
            return
        voted = db.vote("citizen_vote", username, message.from_user.id)
        if voted:
            bot.send_message(message.chat.id, 'Ваш голос учитан')
            return
        bot.send_message(
            message.chat.id, 'У вас больше нет права голосовать')
        return
    bot.send_message(
        message.chat.id, 'Сейчас ночь вы не можете никого выгнать')



@bot.message_handler(commands=["kill"])
def kill(message):
    username = ' '.join(message.text.split(' ')[1:])
    usernames = db.get_all_alive()
    mafia_usernames = db.get_mafia_usernames()
    if night and message.from_user.first_name in mafia_usernames:
        if username not in usernames:
            bot.send_message(message.chat.id, 'Такого имени нет')
            return
        voted = db.vote("mafia_vote", username, message.from_user.id)
        if voted:
            bot.send_message(message.chat.id, 'Ваш голос учтен')
            return
        bot.send_message(
            message.chat.id, 'У вас больше нет права голосовать')
    bot.send_message(message.chat.id, 'Сейчас нельзя убивать')



night = True
def game_loop(message):
    global night, game
    bot.send_message(message.chat.id, "Добро пожаловать в игру! Вам дается 1 минуты, чтоба познакомиться")
    sleep(60)
    while True:
        marycia = get_killed(night)
        bot.send_message(message.chat.id, marycia)
        if night:
            bot.send_message(message.chat.id, "Город засыпает, просыпается мафия. Наступила ночь")
        else:
            bot.send_message(message.chat.id, "Город просыпается. Наступил день")
        winner = db.check_winner()
        if winner == 'Горожане':
            bot.send_message(message.chat.id, "Горожане победили")
            db.clear()
            game = False
            return
        elif winner == 'Мафия':
            bot.send_message(message.chat.id, "Мафия победила")
            db.clear()
            game = False
        db.clear(dead=False)
        night = not night
        sleep(120)
        alive = db.get_all_alive()
        alive = '\n'.join(alive)
        bot.send_message(message.chat.id, f"В игре:\n{alive}")
        sleep(60)

if __name__ == "__main__":
    bot.polling(none_stop=True)