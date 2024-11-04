import databaseManager as db
import config.meet_config as config
import random

# Метод, создающий url встречи. Если аргумент не передан, генерирует случайный url
def create_meeting(name: str = '') -> str:

    name_no_whitespaces = name.replace(" ", "")
    url = ''

    if name_no_whitespaces == '':
        url = f"{config.MEETING_SERVICE_URL}{name_no_whitespaces}"
    else:
        name = generate_meeting_name()
        url = f"{config.MEETING_SERVICE_URL}{name}"

    return url




# Внутренний метод для генерации названия
def generate_meeting_name():
    name = ''
    hyphen_counter_flag = 1

    for _ in range(12):

        name += random.choice(config.ALPHABET)

        hyphen_counter_flag += 1
        if hyphen_counter_flag % 5 == 0 and hyphen_counter_flag != 15:
            name += '-'
            hyphen_counter_flag += 1
    if db.name_exists(name):
        return generate_meeting_name()
    else:
        return name
