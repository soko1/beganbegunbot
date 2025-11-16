#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import re
import configparser
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

# --- Конфиг ---
config = configparser.ConfigParser()
config.read("config.ini")

BOT_TOKEN = config['system']['BOT_API']
DB_VERB = config['system']['DB_VERB']
DB_LOG = config['system']['DB_WRITE_COMMANDS']

# --- Защита от повторного запуска ---
if os.popen(f"ps aux | grep {__file__} | grep -v grep").read().count("python") > 1:
    print("Бот уже запущен")
    exit(1)

# --- Загрузка базы глаголов ---
with open(DB_VERB, 'r', encoding='utf-8') as f:
    VERBS = f.readlines()

# --- Открытие лога ---
log_file = open(DB_LOG, 'a', encoding='utf-8')

# --- Aiogram ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Тексты ---
HELP_TEXT = """
Type any form of an *irregular (!)* verb and get back all three forms together
If you find a mistake or have ideas — write to @rogork
/thanks — supporters
/donate — support the developer
""".strip()

THANKS_TEXT = """
Thanks:
@azinchanka [ideas and English tips]
@gaashek [bot name inventor]
@gilving [code advice]
@vma392 [tried to help with tables]
""".strip()

DONATE_TEXT = """
Support the developer:
https://sakaloucv.github.io/donate
""".strip()

FORBIDDEN = ['хуй', 'пизд', 'ебат', 'fuck', 'suck', 'dick']

# --- Команды ---
@dp.message(Command("start", "help"))
async def cmd_help(message: Message):
    await message.answer(HELP_TEXT, parse_mode="Markdown")

@dp.message(Command("thanks"))
async def cmd_thanks(message: Message):
    await message.answer(THANKS_TEXT)

@dp.message(Command("donate"))
async def cmd_donate(message: Message):
    await message.answer(DONATE_TEXT, parse_mode="Markdown")

@dp.message(Command("count"))
async def cmd_count(message: Message):
    try:
        with open(DB_LOG, 'r', encoding='utf-8') as f:
            content = f.read()
        users = len(set(re.findall(r'(\d+):', content)))
        await message.answer(f"Кол-во уникальных пользователей: {users}")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")

# --- Основной обработчик ---
@dp.message()
async def handle_text(message: Message):
    text = message.text.strip()
    chat_id = message.chat.id

    # Фильтр: только буквы и пробелы
    match = re.search(r'[\w ]+', text)
    if not match:
        await message.answer(HELP_TEXT, parse_mode="Markdown")
        return

    word = match.group().lower()
    if len(word) < 2 or len(word) > 30:
        await message.answer(HELP_TEXT, parse_mode="Markdown")
        return

    # Поддержка "to go"
    parts = word.split()
    if len(parts) == 2 and parts[0] == 'to' and len(parts[1]) > 1:
        word = parts[1]
    elif len(parts) != 1:
        await message.answer(HELP_TEXT, parse_mode="Markdown")
        return
    else:
        word = parts[0]

    # Логирование
    print(f"{chat_id}: {word}", file=log_file, flush=True)

    # Фильтр мата
    if any(bad in word for bad in FORBIDDEN):
        await message.answer("shame on you! :)")
        return

    # Поиск
    if len(word) < 4:
        found = [line for line in VERBS if f'|{word}|' in line]
    else:
        found = [line for line in VERBS if word in line]

    if not found:
        await message.answer(
            f"The word *{word}* is not found.\n"
            "1) misspelled?\n"
            "2) or not irregular?\n"
            "Write @rogork if wrong.\n"
            "/help — more info",
            parse_mode="Markdown"
        )
        return

    # Формируем ответ
    response = ""
    for line in found:
        parts = line.strip().split("|")
        if len(parts) >= 5:
            response += f"{parts[1]}\n{parts[2]}\n{parts[3]}\n({parts[4]})\n\n"
    await message.answer(response.strip(), parse_mode="Markdown")

# --- Запуск ---
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот остановлен.")
    finally:
        log_file.close()
