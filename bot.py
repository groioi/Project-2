import config
import telebot
from telebot import types # кнопки Telegram
from bs4 import  BeautifulSoup as BS
import requests
from telebot import types
from math import *
from sqlighter import *
import sqlite3
from random import randint
from telebot import apihelper
import time
from QIWI import payment_history_last
from urllib3 import disable_warnings, exceptions
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context
disable_warnings(exceptions.InsecureRequestWarning)
bot = telebot.TeleBot(config.BOT_TOKEN)
# инициализируем соединение с БД
db = sqlite3.connect('db.db',check_same_thread=False)
sql = db.cursor()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not(subscriber_exists(message.chat.id)):
        bot.send_message(message.chat.id, 'Вы еще не подписались, оформите ПЛАТНУЮ подписку что бы бот начал свою работу введите команду /subscribe')
    else:
        bot.send_message(message.chat.id, 'Здравствуйте, бот начал свою работу что-бы увидеть список всех команд введите команду /all_commands')

@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    if  not(subscriber_exists(message.chat.id)):
        #если юзера нет в БД, то добавляем его
        markup = types.ReplyKeyboardMarkup(one_time_keyboard = True,resize_keyboard= True, row_width=1)
        phone_button = types.KeyboardButton('/phone', request_contact = True)
        markup.add(phone_button)
        bot.send_message(message.chat.id, 'Нажмите на кнопку что бы мы получили ваш номер телефона ', reply_markup = markup)
    else:
        update_subscribtions(message.chat.id, 1)
@bot.message_handler(content_types = ['contact'])
def contact(message):
            global phone
            phone = message.contact.phone_number
            global random_code
            random_code = randint(100000, 999999)
            markup = types.ReplyKeyboardMarkup(one_time_keyboard = True,resize_keyboard= True, row_width=1)
            check_button = types.KeyboardButton('/check')
            markup.add(check_button)
            bot.send_message(message.chat.id,'Счет\nСумма: 500 руб.\nОплатите подписку на одну неделю по номеру QIWI:+79299779008.В комментариях к платежу отставте :' + str(random_code), reply_markup = markup)
@bot.message_handler(commands=['check'])
def checking(message):
    global random_code
    global phone
    payment(message.chat.id,500,random_code,phone,604800)
    # токен КИВИ и номер телефона
    api_access_token = 'e30683c72403dba0142bbdb4e31414a7'
    my_login = '+79299779008'
    # кол-во перводов
    rows_num = "1"
    # за какой промежуток времени
    next_TxnId, next_TxnDate = "",""
    profile = payment_history_last(my_login, api_access_token, rows_num, next_TxnId, next_TxnDate)
    sum = profile['data'][0]['sum']['amount']
    comment = profile['data'][0]['comment']
    number_phone = profile['data'][0]['account']
    number_phone = str(number_phone)
    number_phone = list(number_phone)
    number_phone.remove('+')
    number_phone = ''.join(number_phone)

    user_id = message.chat.id
    result =  sql.execute(f"SELECT * FROM subscriptions  WHERE user_id = '{user_id}'").fetchall()
    db.commit()

    phone_db = result[0][3]
    sum_db = result[0][4]
    random_code_db = result[0][5]

    if int(comment) == int(random_code_db):
        if int(sum) == int(sum_db):
            if  int(number_phone) == int(phone_db):
                bot.send_message(message.chat.id,'Вы успешно подписались')
                Time(message.chat.id,604800)
    else:
        bot.send_message(message.chat.id,'Что-то пошло не так')


@bot.message_handler(commands=['unsubscribe'])
def unsubscribe(message):
    if  not(subscriber_exists(message.chat.id)):
        #  если юзера нет в БД, то добовляем его с не активной подпиской (запоминаем)
        bot.send_message(message.chat.id,'Вы и так не подписаны')
    else:
        # если он уже есть то обновляем ему статус подписки
        delete_subscribtions(message.chat.id)
        bot.send_message(message.chat.id,'Вы успешно отписаны')

@bot.message_handler(commands=['help'])
def process_help_commands(message):
        if not(subscriber_exists(message.chat.id)):
            bot.send_message(message.chat.id, 'Вы еще не подписались, оформите ПЛАТНУЮ подписку что бы бот начал свою работу')
        else:
            bot.send_message(message.chat.id, 'Этот бот будет присылать вам ссылки на матчи вам необходимо перейти по ссылкам и поставить сумму')

@bot.message_handler(commands=['all_commands'])
def process_all_commands_command(message):
        if not(subscriber_exists(message.chat.id)):
            bot.send_message(message.chat.id, 'Вы еще не подписались, оформите ПЛАТНУЮ подписку что бы бот начал свою работу')
        else:
            bot.send_message(message.chat.id,'букмекерские вилки -- /vilki\n что может делать этот бот -- /help\n подписаться -- /subscribe\n отписаться -- /unsubscribe ' )

URL = 'https://scan-sport.com/vilki/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 OPR/69.0.3686.95 (Edition Yx 02)'
    }
response = requests.get(URL, headers = HEADERS,verify = False)
#soup = BS(open(html_path, 'r'),"html.parser",from_encoding="iso-8859-1")
soup = BS(response.content,'html.parser' ,from_encoding="utf-8")
    #парсер названия матча
items = soup.find('td', class_ = 'event').get_text(strip = True)
nameBK = soup.findAll('a', rel = 'nofollow noreferrer')
    #парсер ссылок на матчи в БК
link = soup.find('a', rel = 'nofollow noreferrer').get('href')
link2 = soup.findAll('a', target = '_blank')
    #название бк
BK = nameBK[0].text
BK2 = nameBK[1].text

@bot.message_handler(commands=['vilki'])
def process_vilki_commands(message):
        if not(subscriber_exists(message.chat.id)):
            bot.send_message(message.chat.id, 'Вы еще не подписались, оформите ПЛАТНУЮ подписку что бы бот начал свою работу')
        else:
            markup_inline = types.InlineKeyboardMarkup()
            calc_button  = types.InlineKeyboardButton(text = 'Калькулятор для подсчёта ставок', callback_data = 'yes')
            markup_inline.add(calc_button)
            bot.send_message(message.chat.id, str(items) + '\n' + str(BK) + ':' + str(link) + '\n' + str(BK2) + ':' + str(link2[1].get('href')), reply_markup = markup_inline)
'''user_vilka = 1/user_k1 + 1/user_k2
user_vilka – Значение, отображающее есть вилка или нет.
Если В>1 – вилки нет,
Если В<1 – вилка есть.
user_k1, user_k2 и т.д. – коэффициенты ставок на взаимоисключающие исходы, сколько вероятных исходов столько и коэффициентов.'''

'''user_stavka1 = (1/user_k1/user_vilka)*user_bank
user_stavka1 – Размер ставки на исход,
user_k1 – коэффициент на исход,
user_vilka – значение вилки, рассчитанное по первой формуле,
user_bank – сумма всех ставок на событие или деньги, которые вы выделили для ставки на вилку.'''
user_bank = ''
user_k1 = ''
user_k2 = ''
user_vilka = ''
user_result = None
@bot.callback_query_handler(func = lambda call:True)
def answer(call):
    if call.data == 'yes':
      msg = bot.send_message(call.message.chat.id , 'Введите ваш банк(Вводите целые числа без знака валюты.Пример : 1000 ')
      bot.register_next_step_handler(msg, process_bank_step)

def process_bank_step(message):
       global user_bank
       try:
           user_bank = int(message.text)
           msg = bot.send_message(message.chat.id, 'Отлично, теперь введите первый коэффициэнт(Указывайте числа с точкой. Пример : 1.5)')
           bot.register_next_step_handler(msg, process_k1_step)
       except Exception as e:
           bot.send_message(message.chat.id,'Данные введены не корректно, Проведите операцию повторно')
def process_k1_step(message):
       global user_k1
       try:
           user_k1 = float(message.text)
           msg = bot.send_message(message.chat.id, 'Oтлично,Tеперь введите второй коэффициэнт')
           bot.register_next_step_handler(msg, process_k2_step)
       except Exception as e:
           bot.send_message(message.chat.id,'Данные введены не корректно, Проведите операцию повторно')


def process_k2_step(message):
            global user_k2
            try:
                user_k2 = float(message.text)
                user_vilka = 1/float(user_k1) + 1/float(user_k2)
                round(user_vilka)
                user_stavka1 = (1/float(user_k1)/float(user_vilka))*float(user_bank)
                round(user_stavka1)
                user_stavka2 = (1/float(user_k2)/float(user_vilka))*float(user_bank)
                round(user_stavka2)
                user_money1 = user_stavka1 * user_k1 - user_bank
                round(user_money1)
                user_money2 = user_stavka2 * user_k2 - user_bank
                round(user_money2)
                bot.send_message(message.chat.id, 'Вы должны поставить на первый исход - ' + str(user_stavka1) + ' руб. '+ '\n' +' Чистая прибыль составит - ' + str(user_money1) + ' руб. '+ '\n'+ ' Вы должны поставить на второй исход - ' + str(user_stavka2) +' руб.'+ '\n'+' Чистая прибыль составит - ' + str(user_money2) + ' руб. ')
            except Exception as e:
                bot.send_message(message.chat.id,'Данные введены не корректно, Проведите  операцию повторно')




if __name__ == '__main__':
    bot.polling(none_stop=True, timeout = 120)
