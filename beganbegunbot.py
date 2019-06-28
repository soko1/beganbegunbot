#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This is a telegram-bot for for learning irregular verbs. 
Type any form of an irregular (!) verb and get back all three forms together
By the way, subscribe: @beganbegunbot

Get the code: https://github.com/soko1/beganbegunbot

# Contacts

@gnupg (telegram)
nullbsd@gmail.com (email)

# Donate

Do you want feed my cat?

Bitcoin: 1NYYFoJiRPnkmFbcv5kYLqwsweix1cVmBT

(Webmoney)

WMZ: Z156396869707
WMR: R409106892241
WME: E320058433666
"""

from __future__ import unicode_literals
import telepot.aio
import os
import configparser
import asyncio
import time
import re
from IPython import embed

config = configparser.ConfigParser()
config.read("config.ini")


# защита от повторного запуска
checkproc = os.popen("ps aux | grep %s" % __file__).read()
if checkproc.count("python") > 1:
    print("Бот уже запущен")
    os._exit(1)

async def main(msg):
#    import IPython; IPython.embed()
    chat_id = msg['chat']['id']
    command = msg['text']

    help = """
Type any form of an *irregular (!)* verb and get back all three forms together

If there are some words missing or you have an idea of improving the bot — be sure to contact me (@gnupg) and  you'll appear (if you wish) here on the list of supporters — /thanks

You can also thank me by giving a positive feedback or buy me a cup of coffee here — /donate
"""

    thanks = """
Thanks:

@azinchanka [идеи и объяснения по тонкостям англ. языка]
@gaashek [оригинальное название для бота, именно она его придумала :)]
@gilving [консультация по изыскам написания кода]
@vma392 [желание помочь с таблицами в telegram, но телега подвела...]
"""

    donate = """
If you want to give thanks buying me a cup of coffee (which I'm really fond of!) — you're welcome:

Paypal: mathematics1688@gmail.com

Bitcoin: `1NYYFoJiRPnkmFbcv5kYLqwsweix1cVmBT`

(Webmoney)
WMZ: `Z156396869707`
WMR: `R409106892241`
WME: `E320058433666`

Any other way: email me at nullbsd@gmail.com or write back here on Telegram @gnupg

Thanks!
"""
    forbidden_words = ['хуй', 'пизд', "ебат", "fuck", "suck", "dick"]

    # вывод справки
    if command.find("/start") != -1:
        await bot.sendMessage(chat_id, help, parse_mode= 'Markdown')
        return
    if command.find("/help") != -1:    
        await bot.sendMessage(chat_id, help, parse_mode= 'Markdown')
        return
    # доска почёта
    if command.find("/thanks") != -1:    
        await bot.sendMessage(chat_id, thanks)
        return
    # пожертвования
    if command.find("/donate") != -1:
        await bot.sendMessage(chat_id, donate, parse_mode= 'Markdown')
        return
    # кол-во уникальных пользователей (незадокументированная команда)
    if command.find("/count") != -1:
        logfile = open(config['system']['DB_WRITE_COMMANDS'], 'r')
        logfile_content = logfile.read()
        logfile.close()
        num_of_uniq_users = len(set(re.findall('\d+:', logfile_content)))
        await bot.sendMessage(chat_id, 'Кол-во уникальных пользователей: ' + str(num_of_uniq_users))
        return    

    # отсеивание мусора из спецсимволов
    search_letters = re.search(r'[\w ]+', command)
    if search_letters:
        command = search_letters.group()
    else:
        await bot.sendMessage(chat_id, help)
        return 

    # отсеивание сообщений менее 2 символов и более 30
    command_len = len(command)
    if command_len < 2 or command_len > 30:
        await bot.sendMessage(chat_id, help)
        return

    # полученная строка
    string = command.lower()

    #
    # проверка на наличие частички to перед глаголом
    #

    string = string.split(" ")
    # если пришло два слова
    if len(string) > 1:
        # где первое слово to, а второе более 1 символа
        if 'to' == string[0] and len(string[1]) > 1:
            # используем для поиска второе слово
             word = string[1]
        else:
            # иначе выводим ошибку
            await bot.sendMessage(chat_id, help)
            return 
    else:
        # если пришло одно слово - испольузем его
        word = string[0]

    # запись лога с присланными сообщениями
    f.write("%s: %s\n" % (chat_id, word))
    f.flush()

    # пасхальное яичко на мат :)
    if [w for w in forbidden_words if w in word]:
        await bot.sendMessage(chat_id, "shame on you! :)")
        return

    #
    # Реализация улучшенного поиска
    #
    # если букв в слове меньше 4
    if len(word) < 4:
        # то ищем лишь это слово целиком
        found_words = [s for s in list_of_words if '|' + word + '|' in s]
    else:
        # иначе будем искать это слово + все однокоренные слова
        found_words = [s for s in list_of_words if word in s]

    # ничего не найдено
    if not found_words:
        message_for_send = """
        The word *%s* is not found in a database. That may happen for two reasons:
1) it is misspelled
2) or it is not an *irregular verb (!)*

If you find it wrong, then be sure to contact me — @gnupg

Get more info — /help
""" % word
        await bot.sendMessage(chat_id, message_for_send, parse_mode= 'Markdown')
        return

    # формирование сообщения
    message_for_send = ""
    for found_word in found_words:
        found_word_split = found_word.split("|")
        message_for_send += (
                            found_word_split[1] + "\n" +
                            found_word_split[2] + "\n" +
                            found_word_split[3] + "\n" + "(" +
                            found_word_split[4] + ")\n\n"
                            )
    await bot.sendMessage(chat_id, message_for_send, parse_mode= 'Markdown')

# активация бота
bot = telepot.aio.Bot(config['system']['BOT_API'])

# создание списка задач
loop = asyncio.get_event_loop()
loop.create_task(bot.message_loop({'chat': main}))

print('Listening ...')

# открытие файла с базой неправильных глаголов
print ("read database")
f = open(config['system']['DB_VERB'], 'r')
list_of_words = f.readlines()
f.close()

f = open(config['system']['DB_WRITE_COMMANDS'], 'a')
print ("read file for write")


try:
	loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    loop.stop()
    loop.close()
