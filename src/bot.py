import asyncio
import logging
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token="6785842829:AAFHVBy_AOseywFfBx6uNxPdOhSHuL7frIA")
# Диспетчер
dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello! I am meeting creator bot, let me help you!")

# Хээндлер на команду /new_meeting
@dp.message(Command("new_meeting"))
async def cmd_start(message: types.Message):
    await message.answer("OK! Let me know at what date do You want to meet!\nWrite it in format DD-MM")
    date_str = message.text

    try:
        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
        await message.reply(date_obj.strftime("%d-%m-%Y"))
    except :
        await message.answer("Please enter a valid date in format DD-MM-YYYY")
def IsDateAware(date):
    return 0
# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())