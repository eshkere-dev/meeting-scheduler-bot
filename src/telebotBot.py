import asyncio
import logging
import datetime
import timeManager as tm
import databaseManager as db
import meetingManager as mm


import telebot

bot = telebot.TeleBot(token="6785842829:AAEzJjOKCXCk2DIcWCRSTCj3RNdM8UW_0yA")
meeting_temp_dict = dict()


def meetings_to_str(meetings):
    meetings_str = ""
    for meeting in meetings:
        meetings_str += f"{meeting}\n"
    return meetings_str


def date_formatter(date_str):
    res = []
    if len(date_str) == 2:
        date = date_str[0]
        time = date_str[1]
    if len(date_str) == 1:
        time = date_str[0]
        date = datetime.date.today().strftime("%d.%m")
    else:
        return res
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
    aliases = message.text.split(" ")

    #TODO: make_validity_checker for aliases

    meeting_temp_dict[message.chat.id]["aliases"] = aliases
    bot.send_message(message.chat.id, "OK! Let me know at what date do You want to meet! \n\n"
                                      "Write it in one of the following formats: \n"
                                      "1. Day.Month Hour:Minute \n"
                                      "2. Hour:Minute (if meeting is today)\n"
                                      "<u>Important note: "
                                      "Meeting must be more than 5 minutes and less than 7 days farther.</u>",
                     parse_mode="HTML")
    bot.register_next_step_handler(message, get_date)
    return


def get_date(message):
    if message.text == "/cancel":
        del meeting_temp_dict[message.chat.id]
        bot.send_message(message.chat.id, "Operation canceled")
        return

    date_str = message.text.split()
    fullDate = date_formatter(date_str)

    if len(fullDate) == 2:
        date = fullDate[0]
        time = fullDate[1]
    elif len(fullDate) == 1:
        date=datetime.date.today().strftime("%d.%m")
        time=fullDate[0]
    else:
        bot.send_message(message.chat.id,
                         "Please enter time in one of the possible formats or use /cancel to cancel. "
                         "\nUse /inst for more information")
        bot.register_next_step_handler(message, get_date)
        return

    if tm.is_date_valid(date) and tm.is_time_valid(time):
        meeting_temp_dict[message.chat.id]["date"] = fullDate
        bot.send_message(message.chat.id, "Now you can enter some details about your meeting. \n"
                                          "Note that details will be used in url, "
                                          "so description should be more than 5 "
                                          "and less than 30 symbols long.")

        bot.register_next_step_handler(message, get_description)
        return


    else:
        bot.send_message(message.chat.id, "Please enter a valid time for your meeting or use /cancel to cancel. \n"
                                          "It must be more than 5 minutes and less than 7 days from now.")
        bot.register_next_step_handler(message, get_date)
        return


def get_description(message):
    description = message.text
    meeting_temp_dict[message.chat.id]["description"] = description
    url = mm.create_meeting(description)
    aliases_string = ", ".join(meeting_temp_dict[message.chat.id]["aliases"])
    if db.add_meeting(meeting_temp_dict[message.chat.id]["date"],
                      meeting_temp_dict[message.chat.id]["aliases"],
                      meeting_temp_dict[message.chat.id]["details"],
                      url):
        bot.send_message(message.chat.id, f"Your meeting was successfully created. Here is some info about it: \n"
                                          f"Date: {meeting_temp_dict[message.chat.id]['date']}, \n"
                                          f"Aliases of members: {aliases_string}, \n"
                                          f"Url: {url}")
    else:
        bot.send_message(message.chat.id, "Oops! Try again later")

    del meeting_temp_dict[message.chat.id]


# Хээндлер на команду /new_meeting
@bot.message_handler(commands=["meet", "new_meeting", "create_meeting"])
def new_meeting(message):
    meeting_temp_dict.update({message.chat.id: {"aliases": [],
                                                "date": [],
                                                "description": ""}})
    bot.send_message(message.chat.id, "Write down aliases of members you want to see on your meeting")
    bot.register_next_step_handler(message, get_aliases)
    return


#Хэндлер на /delete_meeting
#TODO: Rework delete_meeting
def meeting_deleter(message):

    meeting_url = message.text
    if not(meeting_url.startswith("meet.jit.si/")):
        bot.send_message(message.chat.id, "Incorrect url provided")

    if db.get_meeting_creator_id == message.chat.id and db.meeting_exist_by_url(meeting_url):
        if db.delete_meeting_by_url(meeting_url):
            bot.send_message(message.chat.id, "Deleted succesfully")
        else:
            bot.send_message(message.chat.id, "Try again later")



@bot.message_handler(commands=['delete_meeting', 'unmeet'])
def cmd_delete_meeting(message):
    bot.send_message(message.chat.id,
                     "If you want to delete meeting, send me its url in form: meet.jit.si/example-of-meeting")
    bot.register_next_step_handler(message, meeting_deleter)

# Хэндлер на команду /my_meetings
@bot.message_handler(commands=['my_meetings', "my_meets", "meetings"])
def cmd_my_meetings(message):
    meetings = db.get_users_meetings(message.from_user.username)
    if len(meetings) == 0:
        bot.send_message(message.chat.id, "Sorry, it seems that You do not have any meetings.")
    else:
        meetings_str = meetings_to_str(meetings)
        bot.send_message(message.chat.id, "Here are Your meetings:\n", meetings_str)


bot.infinity_polling()
