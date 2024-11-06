import datetime
import telebot
from threading import Thread
import time

import timeManager as tm
import databaseManager as db
import meetingManager as mm
from config.bot_config import TOKEN

bot = telebot.TeleBot(token=TOKEN)


def main():
    meeting_temp_dict = dict()

    def meetings_to_str(meetings):
        meetings_str = ""
        for meeting in meetings:
            meeting = int(meeting)
            meetings_str += f"{tm.to_date(meeting, "%d.%m %H:%M")}\n"
        return meetings_str

    def send_add_notification(aliasArray, CreatorAlias: str, date: str):
        for alias in aliasArray:
            print(alias)
            bot.send_message(db.get_id_by_alias(alias), f"You were invited to join meeting at {date} by {CreatorAlias}")

    def date_formatter(date_str):
        res = []
        if len(date_str) == 2:
            date = date_str[0]
            time = date_str[1]
        elif len(date_str) == 1:
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
        else:
            if db.add_user(id, alias):
                bot.send_message(message.chat.id, "You have been successfully registered. "
                                                  "\nYou can remove registration by typing /unreg command")
            else:
                bot.send_message(message.chat.id, "Registration unsuccessful. Please try again later")

    #Хэндлер на команду /delete_user
    @bot.message_handler(commands=["delete_user", "unreg", "delete_registration"])
    def unreg(message):
        id = message.from_user.id
        alias = message.from_user.username

        if db.user_exists(alias):
            bot.send_message(message.chat.id, "You are not registered yet. Send /start to register")
            return
        else:
            if db.delete_user(id):
                bot.send_message(message.chat.id,
                                 text="You have been successfully removed from the database! \nSee you soon!")
            else:
                bot.send_message(message.chat.id, text="Try again later")

    def get_aliases(message):
        if message.text == "/cancel":
            del meeting_temp_dict[message.chat.id]
            bot.send_message(message.chat.id, "Canceled.")
            return
        aliases = message.text.split(" ")
        for alias in aliases:
            if alias.startswith("@") and not ("," in alias):
                if alias == meeting_temp_dict[message.chat.id]["CreatorAlias"]:
                    continue
                elif db.user_exists(alias):
                    pass
                else:
                    bot.send_message(message.chat.id, f"User {alias} do not exist in our base. \n"
                                                      f"Advise him to join us by using /start")
                    del meeting_temp_dict[message.chat.id]
                    bot.register_next_step_handler(message, get_aliases)
                    return
            else:
                bot.send_message(message.chat.id, "Please type usernames of the participants in following format. \n"
                                                  "Type /cancel to cancel"
                                                  "Example: @first_user @second_user @third_user")
                bot.register_next_step_handler(message, get_aliases)
                return

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
            date = datetime.date.today().strftime("%d.%m")
            time = fullDate[0]
        else:
            bot.send_message(message.chat.id,
                             "Please enter time in one of the possible formats or use /cancel to cancel. "
                             "\nUse /inst for more information")
            bot.register_next_step_handler(message, get_date)
            return

        if tm.is_date_valid(date) and tm.is_time_valid(time):
            meeting_temp_dict[message.chat.id]["date"] = tm.to_unix_from_date(" ".join(fullDate))
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
        if len(description) >= 5 and len(description) <= 30:
            url = mm.create_meeting(description)
            aliases_string = ", ".join(meeting_temp_dict[message.chat.id]["aliases"])
            CreatorAlias = meeting_temp_dict[message.chat.id]["CreatorAlias"]
            CreatorAlias = "@" + CreatorAlias
            meeting_temp_dict[message.chat.id]["creator_id"] = db.get_id_by_alias(CreatorAlias)
            if db.add_meeting(meeting_temp_dict[message.chat.id]["date"],
                              meeting_temp_dict[message.chat.id]["aliases"],
                              meeting_temp_dict[message.chat.id]["description"],
                              url,
                              meeting_temp_dict[message.chat.id]["creator_id"]):
                bot.send_message(message.chat.id,
                                 f"Your meeting was successfully created. Here is some info about it: \n"
                                 f"Date: {tm.to_date(meeting_temp_dict[message.chat.id]['date'])}, \n"
                                 f"Aliases of members: {aliases_string}, \n"
                                 f"Url: {str(url)[8:]}")
                send_add_notification(aliases_string.split(), CreatorAlias,
                                      tm.to_date(meeting_temp_dict[message.chat.id]['date']))
            else:
                bot.send_message(message.chat.id, "Oops! Try again later")

            del meeting_temp_dict[message.chat.id]
        else:
            bot.send_message(message.chat.id, "Please enter a valid description for your meeting \n")
            bot.register_next_step_handler(message, get_description)
            return

    # Хэндлер на команду /new_meeting
    @bot.message_handler(commands=["meet", "new_meeting", "create_meeting"])
    def new_meeting(message):
        if db.user_exists(message.from_user.username):
            bot.send_message(message.chat.id, "Firstly you need to register. Type /start")

        meeting_temp_dict.update({message.chat.id: {"aliases": [],
                                                    "date": [],
                                                    "description": ""}})
        bot.send_message(message.chat.id, "Write down aliases of other members you want to see on your meeting")
        CreatorAlias = message.from_user.username
        meeting_temp_dict[message.chat.id]["CreatorAlias"] = CreatorAlias
        bot.register_next_step_handler(message, get_aliases)
        return

    def meeting_deleter(message):

        meeting_url = message.text
        if not (meeting_url.startswith("meet.jit.si/")):
            bot.send_message(message.chat.id, "Incorrect url provided")
        if db.get_meeting_creator_id(meeting_url) == message.chat.id and db.meeting_url_exists(meeting_url):
            if db.delete_meeting_by_url(meeting_url):
                db.delete_meeting_by_url(meeting_url)
                bot.send_message(message.chat.id, "Deleted succesfully")
            else:
                bot.send_message(message.chat.id, "Try again later")
        else:
            bot.send_message(message.chat.id, "You are not allowed to use this command")

    @bot.message_handler(commands=['delete_meeting', 'unmeet'])
    def cmd_delete_meeting(message):
        meetings = db.get_users_meetings(db.get_id_by_alias("@" + message.from_user.username))
        if len(meetings) == 0:
            bot.send_message(message.chat.id, "Sorry, it seems that You do not have any meetings.")
        else:
            bot.send_message(message.chat.id,
                             "If you want to delete meeting, send me its url in form: meet.jit.si/example-of-meeting")
            bot.register_next_step_handler(message, meeting_deleter)

    # Хэндлер на команду /my_meetings
    @bot.message_handler(commands=['my_meetings', "my_meets", "meetings"])
    def cmd_my_meetings(message):
        meetings = db.get_users_meetings(db.get_id_by_alias("@" + message.from_user.username))
        if len(meetings) == 0:
            bot.send_message(message.chat.id, "Sorry, it seems that You do not have any meetings.")
        else:
            meetings_str = meetings_to_str(meetings)
            bot.send_message(message.chat.id, f"Here are Your meetings:\n {meetings_str}")

    @bot.message_handler(commands=["inst", "help", "info", "get_info"])
    def cmd_info(message):
        bot.send_message(message.chat.id, "/meet - create new meeting\n "
                                          "/my_meetings - get all your meetings\n "
                                          "/delete_meeting - delete your meeting\n "
                                          "/unreg - delete your account from our base\n "
                                          "/help - get this help message")

    bot.infinity_polling()


def passive_notifier():
    while True:

        rows = db.get_all_meetings()

        for row in rows:

            creator_id = row["creator_id"]
            creator_alias = db.get_alias_by_id(creator_id)
            aliases_str = str(row["aliases"]).replace("{", "")
            aliases_str = aliases_str.replace("}", "")
            aliases_list = aliases_str.split(",")
            time_unix = row["time"]
            link_to_meeting = row["link_to_meeting"]

            if abs(tm.date_now() - int(time_unix)) < 60 * 60:
                if abs(tm.date_now() - int(time_unix)) < 15 * 60:
                    for alias in aliases_list:
                        print(alias)
                        user_id = db.get_id_by_alias(alias)

                        if len(str(user_id)) < 5:
                            continue
                        bot.send_message(user_id, f"Looks like you have an upcoming meeting in 15 minutes. "
                                                  f"\nHere is some info about it: "
                                                  f"\nDate: {tm.to_date(int(time_unix))} "
                                                  f"\nCreator: {creator_alias} "
                                                  f"\nOther participants: {", ".join(aliases_list)} "
                                                  f'\n<a href="https{link_to_meeting}">Here is the link</a>',
                                         parse_mode="HTML")
                        db.mark_as_notified15(link_to_meeting)
                else:
                    for alias in aliases_list:
                        user_id = db.get_id_by_alias(alias)
                        if len(str(user_id)) < 5:
                            continue
                        bot.send_message(user_id, f"Looks like you have an upcoming meeting in less than 60 minutes. "
                                                  f"\nHere is some info about it: "
                                                  f"\nDate: {tm.to_date(int(time_unix))} "
                                                  f"\nCreator: {creator_alias} "
                                                  f"\nOther participants: {", ".join(aliases_list)} "
                                                  f"\nLink will be sent 15 minutes before meeting time.")
                        db.mark_as_notified60(link_to_meeting)
        time.sleep(60)


if __name__ == "__main__":
    t_main, t_passive = Thread(target=main), Thread(target=passive_notifier)
    t_main.start(), t_passive.start()
    t_main.join(), t_passive.join()
