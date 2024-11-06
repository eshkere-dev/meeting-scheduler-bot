from datetime import datetime, timedelta
import time


#Проверка правильности ввода даты
def is_date_valid(date_str: str) -> bool:
    date_str = date_str.split('.')
    day = date_str[0]
    month = date_str[1]
    if month in ['1', '3', '5', '7', '8', '10', '12']:
        if 0 < int(day) < 32:
            return True

        else:
            return False
    elif month in ['4', '6', '9', '11']:
        if 0 < int(day) < 31:
            return True
        else:
            return False
    elif month == '2':
        if 0 < int(day) < 29:
            return True
    return False


def is_time_valid(time_str: str) -> bool:
    hour, minute = time_str.split(':')
    if 0 <= int(hour) < 24 and 0 <= int(minute) < 60:
        return True
    return False


#Проверка свободна ли дата,принимает в себя array[date,time]
def is_data_available(dateArray):
    date_string = " ".join(dateArray)
    dt = datetime.strptime(date_string, "%d.%m %H:%M")
    unix_time = int(dt.timestamp())
    current_time = time.time()
    time_difference = current_time - unix_time
    if 300 < time_difference < 604800:
        return True
    return False


def to_unix_from_time(time_str):
    today = datetime.now().date()
    dt = datetime.strptime(time_str, '%H:%M').replace(year=today.year, month=today.month, day=today.day)
    unix_time = int(time.mktime(dt.timetuple()))
    return unix_time


# принимает 'день.месяц часы:минуты' и выводит unix_time
def to_unix_from_date(date_str):
    now = datetime.now()
    current_year = now.year
    dt = datetime.strptime(date_str, f'%d.%m %H:%M').replace(year=current_year)
    unix_time = int(time.mktime(dt.timetuple()))
    return unix_time


def to_unix(date_string, date_format="%d.%m %H:%M"):
    dt = datetime.strptime(date_string, date_format)
    unix_time = int(dt.timestamp())
    return unix_time


def to_date(unix_time, date_format="%d.%m %H:%M"):
    dt = datetime.fromtimestamp(unix_time)
    formatted_date = dt.strftime(date_format)
    return formatted_date


#returns current date in unix format
def date_now() -> int:
    return int(datetime.now().timestamp())


def is_datetime_available(date_str: str) -> bool:
    time = to_unix(date_str)
    timedelta = time - date_now()
    if time > date_now() and 300 < timedelta < 7*24*60*60:
        return True
    return False
