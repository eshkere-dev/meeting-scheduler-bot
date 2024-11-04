from datetime import datetime, timedelta
import time

#Проверка правильности ввода даты
def is_date_valid(date_str:str) -> bool:
    unix_time = to_unix_from_date(date_str)
    current_time = time.time()
    time_difference = unix_time - current_time
    # Проверяем условия: больше 5 минут (300 секунд) и меньше 7 дней (604800 секунд)
    if 300 < time_difference < 604800:
        return True
    return False


#Проверка правильности ввода времени
def is_time_valid(time_str:str) -> bool:
    unix_time = to_unix_from_time(time_str)
    current_time = time.time()
    time_difference = unix_time - current_time
    # Проверяем условия: больше 5 минут (300 секунд) и меньше 7 дней (604800 секунд)
    if 300 < time_difference:
        return True
    return False


#Проверка свободна ли дата,принимает в себя array[date,time]
def is_data_available(dateArray):
    date_string = " ".join(dateArray)
    dt = datetime.strptime(date_string, "%d.%m %H:%M")
    dt -= timedelta(hours=3)
    unix_time = int(dt.timestamp())
    current_time = time.time() + 10800
    time_difference = current_time - unix_time
    if 300 < time_difference < 604800:
        return True
    return False


def to_unix_from_time(time_str):
    today = datetime.now().date()
    dt = datetime.strptime(time_str, '%H:%M').replace(year=today.year, month=today.month, day=today.day)
    dt -= timedelta(hours=3)
    unix_time = int(time.mktime(dt.timetuple()))
    return unix_time


# принимает 'день.месяц часы:минуты' и выводит unix_time
def to_unix_from_date(date_str):
    now = datetime.now()
    current_year = now.year
    dt = datetime.strptime(date_str, f'%d-%m %H:%M').replace(year=current_year)
    dt -= timedelta(hours=3)
    unix_time = int(time.mktime(dt.timetuple()))
    return unix_time