from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

button_weather = KeyboardButton('Погода')
button_currency = KeyboardButton('Валюта')
button_cats = KeyboardButton('Котик')
button_poll = KeyboardButton('Создать опрос')
button_bar = ReplyKeyboardMarkup(resize_keyboard=True)
button_bar.add(button_weather, button_currency, button_cats, button_poll)

pool_add_option = KeyboardButton('Добавить вариант')
save_poll = KeyboardButton('Сохранить опрос')
poll_botton_bar = ReplyKeyboardMarkup(resize_keyboard=True)
poll_botton_bar.add(save_poll)