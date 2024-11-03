import asyncio
import logging
import datetime
import timeManager as tm
import databaseManager as db

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token="6785842829:AAFHVBy_AOseywFfBx6uNxPdOhSHuL7frIA")
# Диспетчер
dp = Dispatcher()

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
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello! I am meeting creator bot, let me help you!")

# Хээндлер на команду /new_meeting
@dp.message(Command("new_meeting"))
async def cmd_new_meeting(message: types.Message):
    fullDate=[]
    await message.answer("Write down aliases of members.")
    aliases=message.text.split(" ")
    await message.answer("OK! Let me know at what date do You want to meet!\nWrite it in format Day-Month Hour-Minute or Hour-Minute if meeting is today.")
    date_str=message.text.split()
    fullDate=date_formatter(date_str)
    if len(fullDate)!=0:
        date=fullDate[0]
        time=fullDate[1]
    else:
        await message.answer("Please enter a valid date in format Day-Month Hour-Minute or Hour-Minute if meeting is today.")
    if tm.IsDateValid(date) and tm.IsTimeValid(time):
        if tm.IsDataAvailable(fullDate):
            db.add_meeting(fullDate, aliases)
        else:
            await message.answer("Sorry, this time is not available.")
    else:
        await message.answer("Please enter a valid date in format Day-Month Hour-Minute or Hour-Minute if meeting is today.")
#Хэндлер на /delete_meeting
@dp.message((Command("delete_meeting")))
async def cmd_delete_meeting(message: types.Message):
    await message.answer("Please enter a date in format Day-Month Hour-Minute or Hour-Minute if meeting is today to delete it.")
    fullDate = []
    date_str = message.text.split()
    fullDate = date_formatter(date_str)
    if len(fullDate) != 0:
        date = fullDate[0]
        time = fullDate[1]
    else:
        await message.answer(
            "Please enter a valid date in format Day-Month Hour-Minute or Hour-Minute if meeting is today.")
    if tm.IsDateValid(date) and tm.IsTimeValid(time):
        if not tm.IsDataAvailable(fullDate):
            db.delete_meeting(fullDate)
        else:
            await message.answer("Sorry, there is no such meeting.")
    else:
        await message.answer(
            "Please enter a valid date in format Day-Month Hour-Minute or Hour-Minute if meeting is today.")
# Запуск процесса поллинга новых апдейтов
@dp.message((Command("my_meetings")))
async def cmd_my_meetings(message: types.Message):
    meetings=db.get_users_meetings(message.from_user.username)
    if len(meetings)==0:
        await message.answer("Sorry, it seems that You do not have any meetings.")
    else:
        meetings_str=meetings_to_str(meetings)
        await message.answer("Here are Your meetings:\n",meetings_str)
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())