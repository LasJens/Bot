import json
import requests
import datetime
import telebot
from telebot import types

bot = telebot.TeleBot('6939301069:AAH-w-vYunyHQfp84B6DiyYm6cBiRjMTJ80')

def load_exchange(url):
    return json.loads(requests.get(url).text)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, "Привет! Я бот, могу помочь отследить рейс или получить информацию о нём\n"
                                           "/all_possible - все возможности")

@bot.message_handler(commands=['all_possible'])
def get_text_messages(message):
    bot.send_message(message.from_user.id, "Список возможностей:\n"
                                           "/all_possible - список возможностей\n"
                                           "/flight_radar - информация о текущем полёте + координаты\n"
                                           "/fast_departure - вылет через 2 часа из указаного аэропорта\n"
                                           "/preflight - полная информация о рейсе\n"
                                           "/curflight - параметры текущего полёта")

@bot.message_handler(commands=['flight_radar'])
def fl_helper(message):
    bot.send_message(message.from_user.id, 'Введите номер рейса и код аэропорта отправления в формате ААА через пробел')
    bot.register_next_step_handler(message, flight_radar)
def flight_radar(message):
    try:
        inputed = message.text
        lst = list(inputed.split())
        url = "https://airlabs.co/api/v9/flights?dep_iata=" + lst[1] + "&api_key=3215bdf7-f61c-4a92-86d2-1b24901af76c"
        url_2 = "https://airlabs.co/api/v9/airlines?api_key=3215bdf7-f61c-4a92-86d2-1b24901af76c"
        url_3 = "https://airlabs.co/api/v9/airports?api_key=3215bdf7-f61c-4a92-86d2-1b24901af76c"
        url_4 = "https://airlabs.co/api/v9/countries?api_key=3215bdf7-f61c-4a92-86d2-1b24901af76c"
        upload = load_exchange(url)
        upload_2 = load_exchange(url_2)
        upload_3 = load_exchange(url_3)
        upload_4 = load_exchange(url_4)
        answer = '\n'
        coords_1 = ''
        coords_2 = ''
        airline = ''
        dep_airport = ''
        arr_airport = ''
        dep_country = ''
        arr_country = ''
        fl_type = ''
        for i in upload["response"]:
            if i["flight_iata"] == lst[0]:
                if i["status"] == "en-route":
                    for j in upload_2["response"]:
                        if j["icao_code"] == i["airline_icao"]:
                            airline = j["name"]
                            break
                    for j in upload_3["response"]:
                        if j["iata_code"] == i["dep_iata"]:
                            dep_airport = j["name"]
                            dep_country = j["country_code"]
                            for k in upload_4["response"]:
                                if k["code"] == dep_country:
                                    dep_country = k["name"]
                                    break
                    for j in upload_3["response"]:
                        if j["iata_code"] == i["arr_iata"]:
                            arr_airport = j["name"]
                            arr_country = j["country_code"]
                            for k in upload_4["response"]:
                                if k["code"] == arr_country:
                                    arr_country = k["name"]
                                    break
                    if dep_country == arr_country:
                        fl_type = "Внутренний перелёт"
                    else:
                        fl_type = "Международный перелёт"
                    coords_1 = i["lat"]
                    coords_2 = i["lng"]
                    answer = fl_type + '\n' + "Cамолёт " + i["aircraft_icao"] + " авиакомпании " + airline + " выполняет полёт по маршруту:\n" + dep_airport + " (" + dep_country + ")"  " -->\n" + arr_airport + " (" + arr_country + ")" "\nКоординаты:\n" + str(coords_1) + '\n' + str(coords_2)
                    bot.send_message(message.from_user.id, answer)
                    bot.send_location(message.from_user.id, coords_1, coords_2)
                    break
    except:
        bot.send_message(message.from_user.id, "Неверно введены данные, либо этот рейс сейчас не выполняется\n/all_possible")



@bot.message_handler(commands=['fast_departure'])
def fd_helper(message):
    bot.send_message(message.from_user.id, "Из какого aэропорта вы хотите вылететь?\n"
                                           "Введите код аэропорта в формате ААА\n"
                                           "(Aэропорт в вашем часовом поясе!)")
    bot.register_next_step_handler(message, fast_departure)
def fast_departure(message):
    try:
        inputed = message.text
        url_schedule = "https://airlabs.co/api/v9/schedules?dep_iata=" + inputed + "&api_key=3215bdf7-f61c-4a92-86d2-1b24901af76c"
        url_2 = "https://airlabs.co/api/v9/airlines?api_key=3215bdf7-f61c-4a92-86d2-1b24901af76c"
        url_3 = "https://airlabs.co/api/v9/airports?api_key=3215bdf7-f61c-4a92-86d2-1b24901af76c"
        url_4 = "https://airlabs.co/api/v9/countries?api_key=3215bdf7-f61c-4a92-86d2-1b24901af76c"
        upload_s = load_exchange(url_schedule)
        upload_2 = load_exchange(url_2)
        upload_3 = load_exchange(url_3)
        upload_4 = load_exchange(url_4)
        answer = '\n'
        flag = 0
        now = datetime.datetime.now()
        current_day = now.day
        current_hour = now.hour
        current_minute = now.minute
        airline = ''
        dep_airport = ''
        arr_airport = ''
        dep_country = ''
        arr_country = ''
        fl_type = ''
        for i in upload_3["response"]:
            if i["iata_code"] == inputed:
                dep_airport = i["name"]
                dep_country = i["country_code"]
                for k in upload_4["response"]:
                    if k["code"] == dep_country:
                        dep_country = k["name"]
                        break
                break
        for i in upload_s["response"]:
            lst_1 = list(i["dep_time"].split())
            lst_2 = list(lst_1[1].split(":"))
            lst_3 = list(lst_1[0].split('-'))
            base_hour = int(lst_2[0])
            base_minute = int(lst_2[1])
            base_day = int(lst_3[2])
            if base_hour >= int(current_hour) + 2 and base_day >= int(current_day):
                for j in upload_2["response"]:
                    if j["icao_code"] == i["airline_icao"]:
                        airline = j["name"]
                        break
                for j in upload_3["response"]:
                    if j["iata_code"] == i["arr_iata"]:
                        arr_airport = j["name"]
                        arr_country = j["country_code"]
                        for k in upload_4["response"]:
                            if k["code"] == arr_country:
                                arr_country = k["name"]
                                break
                if dep_country == arr_country:
                    fl_type = "Внутренний перелёт"
                else:
                    fl_type = "Международный перелёт"
                answer = fl_type + '\n' + "Дата вылета: " + i["dep_time"] + '\n' + dep_airport + " (" + dep_country + ")"  " -->\n" + arr_airport + " (" + arr_country + ")" + '\n' + "авиакомпанией " + airline
                bot.send_message(message.from_user.id, answer)
                flag = flag + 1
                if flag == 10:
                    break
            elif base_hour >= int(current_hour) - 22 and base_day > int(current_day):
                for j in upload_2["response"]:
                    if j["icao_code"] == i["airline_icao"]:
                        airline = j["name"]
                        break
                for j in upload_3["response"]:
                    if j["iata_code"] == i["arr_iata"]:
                        arr_airport = j["name"]
                        arr_country = j["country_code"]
                        for k in upload_4["response"]:
                            if k["code"] == arr_country:
                                arr_country = k["name"]
                                break
                if dep_country == arr_country:
                    fl_type = "Внутренний перелёт"
                else:
                    fl_type = "Международный перелёт"
                answer = fl_type + '\n' + "Дата вылета: " + i["dep_time"] + '\n' + dep_airport + " (" + dep_country + ")"  " -->\n" + arr_airport + " (" + arr_country + ")" + '\n' + "авиакомпанией " + airline
                bot.send_message(message.from_user.id, answer)
                flag = flag + 1
                if flag == 10:
                    break
    except:
        bot.send_message(message.from_user.id, "Неверно указан аэропорт, либо в данный момент подходящих вылетов нет.\n/all_possible")

@bot.message_handler(commands=['preflight'])
def pf_helper(message):
    bot.send_message(message.from_user.id, "Введите номер рейса и код аэропорта отправления в формате ААА через пробел")
    bot.register_next_step_handler(message, preflight)
def preflight(message):
    try:
        inputed = message.text
        lst = list(inputed.split())
        url_schedule = "https://airlabs.co/api/v9/schedules?dep_iata=" + lst[1] + "&api_key=3215bdf7-f61c-4a92-86d2-1b24901af76c"
        url_2 = "https://airlabs.co/api/v9/airlines?api_key=3215bdf7-f61c-4a92-86d2-1b24901af76c"
        url_3 = "https://airlabs.co/api/v9/airports?api_key=3215bdf7-f61c-4a92-86d2-1b24901af76c"
        url_4 = "https://airlabs.co/api/v9/countries?api_key=3215bdf7-f61c-4a92-86d2-1b24901af76c"
        upload_s = load_exchange(url_schedule)
        upload_2 = load_exchange(url_2)
        upload_3 = load_exchange(url_3)
        upload_4 = load_exchange(url_4)
        answer = '\n'
        dep_airport = ''
        dep_country = ''
        dep_gate = ''
        dep_terminal = ''
        dep_time = ''
        duration = ''
        delay = ''
        arr_airport = ''
        arr_country = ''
        arr_gate = ''
        arr_terminal = ''
        arr_baggage = ''
        arr_time = ''
        airline = ''
        fl_type = ''
        for i in upload_s["response"]:
            if i["flight_iata"] == lst[0]:
                if i["dep_terminal"] == None:
                    dep_terminal = "Пока неизвестно"
                else:
                    dep_terminal = i["dep_terminal"]
                if i["dep_gate"] == None:
                    dep_gate = "Пока неизвестно"
                else:
                    dep_gate = i["dep_gate"]
                if i["arr_terminal"] == None:
                    arr_terminal = "Пока неизвестно"
                else:
                    arr_terminal = i["arr_terminal"]
                if i["arr_gate"] == None:
                    arr_gate = "Пока неизвестно"
                else:
                    arr_gate = i["arr_gate"]
                if i["arr_baggage"] == None:
                    arr_baggage = "Пока неизвестно"
                else:
                    arr_baggage = i["arr_baggage"]
                for j in upload_2["response"]:
                    if j["icao_code"] == i["airline_icao"]:
                        airline = j["name"]
                        break
                for j in upload_3["response"]:
                    if j["iata_code"] == i["dep_iata"]:
                        dep_airport = j["name"]
                        dep_country = j["country_code"]
                        for k in upload_4["response"]:
                            if k["code"] == dep_country:
                                dep_country = k["name"]
                                break
                for j in upload_3["response"]:
                    if j["iata_code"] == i["arr_iata"]:
                        arr_airport = j["name"]
                        arr_country = j["country_code"]
                        for k in upload_4["response"]:
                            if k["code"] == arr_country:
                                arr_country = k["name"]
                                break
                if i["delayed"] == None:
                    delay = "не задержан"
                else:
                    delay_h = i["delayed"] // 60
                    delay_m = i["delayed"] - delay_h * 60
                    if delay_m < 10:
                        delay = str(delay_h) + ':' + '0' + str(delay_m)
                    else:
                        delay = str(delay_h) + ':' + str(delay_m)
                list_dep_time = list(i["dep_time"].split())
                list_arr_time = list(i["arr_time"].split())
                if dep_country == arr_country:
                    fl_type = "Внутренний перелёт"
                else:
                    fl_type = "Международный перелёт"
                answer = "Информация о полёте:\n" + fl_type + '\n' + "Авиакомпания: " + airline + '\n' + "Время вылета: " + list_dep_time[1]  + '\n' + "Задержка: " + delay + '\n' + "Время прилёта: " + list_arr_time[1] + '\n' + "Аэропорт отправления: " + dep_airport + '\n' + "Страна отправления: " + dep_country + '\n' + "Терминал отправления: " + dep_terminal + '\n' + "Выход на посадку: " + dep_gate + '\n' + "Аэропорт прибытия: " + arr_airport + '\n' + "Страна прибытия: " + arr_country + '\n' + "Терминал прибытия: " + arr_terminal + '\n' + "Выход из самолета: " + arr_gate + '\n' + "Багажная лента: " + arr_baggage
                bot.send_message(message.from_user.id, answer)
                break
    except:
        bot.send_message(message.from_user.id, "Неверно введены данные, либо подходящего вылета нет\n/all_possible")


@bot.message_handler(commands=['curflight'])
def cf_helper(message):
    bot.send_message(message.from_user.id, "Введите номер рейса и код аэропорта отправления в формате ААА через пробел")
    bot.register_next_step_handler(message, curflight)
def curflight(message):
    try:
        inputed = message.text
        lst = list(inputed.split())
        url = "https://airlabs.co/api/v9/flights?dep_iata=" + lst[1] + "&api_key=3215bdf7-f61c-4a92-86d2-1b24901af76c"
        url_2 = "https://airlabs.co/api/v9/airlines?api_key=3215bdf7-f61c-4a92-86d2-1b24901af76c"
        url_3 = "https://airlabs.co/api/v9/airports?api_key=3215bdf7-f61c-4a92-86d2-1b24901af76c"
        url_4 = "https://airlabs.co/api/v9/countries?api_key=3215bdf7-f61c-4a92-86d2-1b24901af76c"
        upload = load_exchange(url)
        upload_2 = load_exchange(url_2)
        upload_3 = load_exchange(url_3)
        upload_4 = load_exchange(url_4)
        answer = '\n'
        horizontal_speed = ''
        vertical_speed = ''
        info = ''
        airline = ''
        dep_airport = ''
        arr_airport = ''
        dep_country = ''
        arr_country = ''
        fl_type = ''
        for i in upload["response"]:
            if i["flight_iata"] == lst[0]:
                if i["status"] == "en-route":
                    for j in upload_2["response"]:
                        if j["icao_code"] == i["airline_icao"]:
                            airline = j["name"]
                            break
                    for j in upload_3["response"]:
                        if j["iata_code"] == i["dep_iata"]:
                            dep_airport = j["name"]
                            dep_country = j["country_code"]
                            for k in upload_4["response"]:
                                if k["code"] == dep_country:
                                    dep_country = k["name"]
                                    break
                    for j in upload_3["response"]:
                        if j["iata_code"] == i["arr_iata"]:
                            arr_airport = j["name"]
                            arr_country = j["country_code"]
                            for k in upload_4["response"]:
                                if k["code"] == arr_country:
                                    arr_country = k["name"]
                                    break
                    if dep_country == arr_country:
                        fl_type = "Внутренний перелёт"
                    else:
                        fl_type = "Международный перелёт"
                    horizontal_speed = i["speed"]
                    vertical_speed = i["v_speed"]
                    if horizontal_speed >= 700 and vertical_speed > 0:
                        info = "Самолёт летит с крейсерской скоростью и набирает высоту.\nСкорость полёта: " + str(horizontal_speed) + " км/ч\n" + "Скорость подъёма: " + str(vertical_speed) + " км/ч"
                    elif horizontal_speed >= 700 and vertical_speed < 0:
                        info = "Самолёт летит с крейсерской скоростью и снижается.\nСкорость полёта: " + str(horizontal_speed) + " км/ч\n" + "Скорость снижения: " + str(abs(vertical_speed)) + " км/ч"
                    elif horizontal_speed < 700 and vertical_speed < 0:
                        info = "Самолёт снижается.\nСкорость полёта: " + str(horizontal_speed) + " км/ч\n" + "Скорость снижения: " + str(abs(vertical_speed)) + " км/ч"
                    elif horizontal_speed < 700 and vertical_speed > 0:
                        info = "Самолёт взлетает.\nСкорость полёта: " + str(horizontal_speed) + " км/ч\n" + "Скорость подъёма: " + str(vertical_speed) + " км/ч"
                    elif horizontal_speed >= 700 and vertical_speed == 0:
                        info = "Самолёт летит с крейсерской скоростью.\nСкорость полёта: " + str(horizontal_speed) + " км/ч\n" + "Скорость по вертикали: " + str(vertical_speed) + " км/ч"
                    elif horizontal_speed < 700 and vertical_speed == 0:
                        info = "Самолёт летит с низкой скоростью.\nСкорость полёта: " + str(horizontal_speed) + " км/ч\n" + "Скорость по вертикали: " + str(vertical_speed) + " км/ч"
                    answer = fl_type + '\n' + "Cамолет " + i["aircraft_icao"] + " авиакомпании " + airline + " выполняет полет по маршруту:\n" + dep_airport + " (" + dep_country + ")"  " -->\n" + arr_airport + " (" + arr_country + ")" + '\n' + info
                    bot.send_message(message.from_user.id, answer)
                    break
    except:
        bot.send_message(message.from_user.id, "Неверно введены данные, либо этот рейс сейчас не выполняется\n/all_possible")


@bot.message_handler(content_types = ['text'])
def get_text_messages(message):
    if message.text == "Привет":
        bot.send_message(message.from_user.id, "Привет, чем я могу помочь?\n/all_possible - все возможности")
    else:
        bot.send_message(message.from_user.id, "Не понимаю.\n/all_possible - все возможности")

bot.polling(none_stop=True, interval=0)