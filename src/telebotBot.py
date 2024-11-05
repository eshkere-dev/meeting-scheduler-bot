import asyncio
import logging
import datetime
import timeManager as tm
import databaseManager as db
import bot_config as cfg

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

import telebot

bot = telebot.TeleBot(token="6785842829:AAFHVBy_AOseywFfBx6uNxPdOhSHuL7frIA")

def meetings_to_str(meetings):
    meetings_str = ""
    for meeting in meetings:
        meetings_str += f"{meeting}\n"
    return meetings_str


def date_formatter(date_str):
    res=[]
    if len(date_str)==2:
        date=date_str[0]
        time=date_str[1]
    if len(date_str)==1:
        time=date_str[0]
        date=datetime.date.now.strftime("%m-%d")
    else: return res
    res.append(date)
    res.append(time)
    return res

# Хэндлер на команду /start
@bot.message_handler(commands=['start', 'reg'])
def start(message):
    bot.send_message(message.chat.id, "Hello! I'm meeting creator bot, I'm here to help you!. "
                                      "\nSend /inst to receive instructions on how to create meeting  ")

    id = message.from_user.id
    alias = message.from_user.username

    if db.user_exists(alias):
        return

    if db.add_user(id, alias):
        bot.send_message(message.chat.id, "You have been successfully registered. "
                                          "\nYou can remove registration by typing /unreg command")
    else:
        bot.send_message(860597138, "register unsuccessful")
        bot.send_message(message.chat.id, "Registration unsuccessful. Please try again later")


#Хэндлер на команду /delete_user
@bot.message_handler(commands=["delete_user", "unreg", "delete_registration"])
def unreg(message):

    id = message.from_user.id
    alias = message.from_user.username

    if db.user_exists(alias):
        bot.send_message(message.chat.id, "You are not registered yet. Send /start to register")
        return

    if db.delete_user(id):
        bot.send_message(message.chat.id, text="You have been successfully removed from the database! \nSee you soon!")
    else:
        bot.send_message(message.chat.id, text="Try again later")


def get_aliases(message):
    pass
    #TODO: CHANGE GET ALIASES METHOD l:81
# Хээндлер на команду /new_meeting
@bot.message_handler(commands=["meet", "new_meeting", "create_meeting"])
def new_meeting(message):

    fullDate=[]
    bot.send_message(message.chat.id, "Write down aliases of members.")
    bot.register_next_step_handler(message, )
    aliases=message.text.split(" ")
    bot.send_message(message.chat.id, "OK! Let me know at what date do You want to meet!\nWrite it in format Day-Month Hour-Minute or Hour-Minute if meeting is today.")
    date_str=message.text.split()
    fullDate=date_formatter(date_str)
    if len(fullDate)!=0:
        date=fullDate[0]
        time=fullDate[1]
    else:
        bot.send_message(message.chat.id, "Please enter a valid date in format Day-Month Hour-Minute or Hour-Minute if meeting is today.")
    if tm.is_date_valid(date) and tm.is_time_valid(time):
        if tm.is_data_available(fullDate):
            bot.send_message(message.chat.id, "Enter some details about meeting.")
            details = message.text
            db.add_meeting(fullDate, aliases,details )
        else:
            bot.send_message(message.chat.id, "Sorry, this time is not available.")
    else:
        bot.send_message(message.chat.id, "Please enter a valid date in format Day-Month Hour-Minute or Hour-Minute if meeting is today.")

#Хэндлер на /delete_meeting
@bot.message_handler(commands=['delete_meeting', 'unmeet'])
def cmd_delete_meeting(message):

    bot.send_message(message.chat.id, "Please enter a date in format Day-Month Hour-Minute or Hour-Minute if meeting is today to delete it.")
    fullDate = []
    date_str = message.text.split()
    fullDate = date_formatter(date_str)

    if len(fullDate) != 0:
        date = fullDate[0]
        time = fullDate[1]
    else:
        bot.send_message(message.chat.id, 
            "Please enter a valid date in format Day-Month Hour-Minute or Hour-Minute if meeting is today.")


    if tm.is_date_valid(date) and tm.is_time_valid(time):
        if not tm.is_data_available(fullDate):
            db.delete_meeting(fullDate)
        else:
            bot.send_message(message.chat.id, "Sorry, there is no such meeting.")
    else:
        bot.send_message(message.chat.id, 
            "Please enter a valid date in format Day-Month Hour-Minute or Hour-Minute if meeting is today.")

# Хэндлер на команду /my_meetings
@bot.send_message(commands=['my_meetings'])
def cmd_my_meetings(message: types.Message):
    meetings=db.get_users_meetings(message.from_user.username)
    if len(meetings)==0:
        bot.send_message(message.chat.id, "Sorry, it seems that You do not have any meetings.")
    else:
        meetings_str=meetings_to_str(meetings)
        bot.send_message(message.chat.id, "Here are Your meetings:\n",meetings_str)

bot.infinity_polling()


if __name__ == "__main__":
    asyncio.run(main())