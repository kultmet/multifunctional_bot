import logging
import os

import aiohttp
from aiohttp.client import ContentTypeError

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text, state
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from dotenv import load_dotenv

from buttons import button_bar, poll_botton_bar
from weater_api import Weather
from exchnge import exchange
from constants import *

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
API_WEATHER = os.getenv('WEATHER_API_KEY')
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class DataInput(state.StatesGroup):
    city_name = state.State()
    currency_values = state.State()
    poll_question = state.State()
    option = state.State()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply(f'Здравствуйте! {message.from_user.username}. Выбирайте!', reply_markup=button_bar)

@dp.message_handler(Text('Погода'))
async def weather(message: types.Message):
    await bot.send_message(message.from_user.id,'Введите интересующий вас город...')
    await DataInput.city_name.set()

    @dp.message_handler(state=DataInput.city_name)
    async def get_weather(message: types.Message, state):
        city_name = message.text
        async with aiohttp.ClientSession() as session:
            url = WEATHER_URL
            params = {'q': city_name, 'appid': API_WEATHER, 'units': 'metric', 'lang': 'ru'}
            async with session.get(url=url, params=params) as response:
                try:
                    weather_json = await response.json()
                except ContentTypeError:
                    await bot.send_message(message.from_user.id, 'Сервер все!!!')
                weather = Weather(weather_json)
                await message.answer(weather, reply_markup=button_bar)
        await state.finish()

@dp.message_handler(Text('Валюта'))
async def currency(message: types.Message):
    blank = {}
    async with aiohttp.ClientSession() as session:
        url = CURRENCY_URL
        async with session.get(url=url) as response:
            try:
                courses_json = await response.json(content_type='application/javascript')
            except ContentTypeError:
                await bot.send_message(message.from_user.id, 'Сервер все!!!')
            blank = courses_json
    await bot.send_message(message.from_user.id, INVATION)
    await DataInput.currency_values.set()

    @dp.message_handler(state=DataInput.currency_values)
    async def exchange_recive(message: types.Message, state):
        try:
            first_ticket, end_ticket, amount = message.text.split(' ')
        except ValueError:
            await message.answer(VALUE_ERR_MESSAGE, reply_markup=button_bar)
            return
        try:
            currency_set = blank['rates']
        except KeyError:
            message.answer(KEY_ERR_MESSAGE, reply_markup=button_bar)
        else:
            try:
                result = exchange(first_ticket.upper(), end_ticket.upper(), float(amount), currency_set)
            except ValueError:
                await message.answer(VALUE_ERR_MESSAGE, reply_markup=button_bar)
                return
            await message.answer(result, reply_markup=button_bar)
            await state.finish()

@dp.message_handler(Text('Котик'))
async def cat(message: types.Message):
    """Bot thinks cats are cute."""
    async with aiohttp.ClientSession() as session:
        url = CATS_URL
        async with session.get(url=url) as response:
            try:
                cat_json = await response.json()
            except ContentTypeError:
                await bot.send_message(message.from_user.id, 'Сервер все!!!')
            for cat in cat_json:
                await bot.send_photo(message.from_user.id, cat['url'], reply_markup=button_bar)

@dp.message_handler(Text('Создать опрос'))
async def create_poll(message: types.Message):
    """Initiates the creation of a poll."""
    await message.answer('Введите вопрос', reply_markup=ReplyKeyboardRemove())
    await DataInput.poll_question.set()

@dp.message_handler(state=DataInput.poll_question)
async def question(message: types.Message, state: FSMContext):
    """Adds question and redirects to next step (add otions for poll)."""
    answer = message.text
    await state.update_data(question=answer)
    await message.answer('Добавьте вариант ответа, или сохраните опрос', reply_markup=poll_botton_bar)
    await DataInput.next()
    await state.update_data(options=[])

@dp.message_handler(state=DataInput.option)
async def option(message: types.Message, state: FSMContext):
    """Adds option or saves poll."""
    if message.text == 'Сохранить опрос':
        await message.answer(f'Опрос сохранен и отправлен в канал {CHANNEL_URL}', reply_markup=button_bar)
        data = await state.get_data()
        # await message.answer(data['question'], data['options'])
        await bot.send_message(CHANNEL_ID, 'Пройдите опрос!')
        await bot.send_poll(CHANNEL_ID, data['question'], data['options'])
        await state.finish()
        return
    data = await state.get_data()
    options: list = data['options']
    answer = message.text
    options.append(answer)
    await state.update_data(options=options)
    await message.answer('Добавьте еще вариант ответа, или сохраните опрос', reply_markup=poll_botton_bar)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
