import logging

import aiohttp
from aiohttp.client import ContentTypeError

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text, state
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove

from buttons import button_bar, poll_botton_bar, currency_button_bar
from weater_api import Weather
from exchnge import exchange
from constants import *
from utils import add_to_redis, generate_buttons

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class DataInput(state.StatesGroup):
    city_name = state.State()
    current_currency = state.State()
    required_currency = state.State()
    amount_currency = state.State()
    poll_question = state.State()
    option = state.State()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply(
        f'Здравствуйте! {message.from_user.username}. Выбирайте!',
        reply_markup=button_bar
    )


@dp.message_handler(Text('Погода'))
async def weather(message: types.Message):
    """Asks city name."""
    await bot.send_message(
        message.from_user.id,
        'Введите интересующий вас город',
        reply_markup=ReplyKeyboardRemove()
    )
    await DataInput.city_name.set()


@dp.message_handler(state=DataInput.city_name)
async def get_weather(message: types.Message, state: FSMContext):
    city_name = message.text
    async with aiohttp.ClientSession() as session:
        url = WEATHER_URL
        params = WEATHER_PARAMS
        params['q'] = city_name
        async with session.get(url=url, params=params) as response:
            try:
                weather_json = await response.json()
            except ContentTypeError:
                await bot.send_message(
                    message.from_user.id,
                    'Сервер все!!!',
                    reply_markup=button_bar
                )
            weather = Weather(weather_json)
            await message.answer(weather, reply_markup=button_bar)
    await state.finish()


@dp.message_handler(Text('Валюта'))
async def currency(message: types.Message):
    """Executes the get-request to currency API and  asks current currency."""
    async with aiohttp.ClientSession() as session:
        url = CURRENCY_URL
        async with session.get(url=url) as response:
            try:
                courses_json = await response.json(
                    content_type='application/javascript'
                )
                rates = courses_json['rates']
            except ContentTypeError:
                await bot.send_message(
                    message.from_user.id,
                    'Сервер все!!!',
                    reply_markup=button_bar
                )
            await add_to_redis(rates)
            generate_buttons(rates)
    await bot.send_message(
        message.from_user.id,
        'Выберете текущую валюту',
        reply_markup=currency_button_bar
    )
    await DataInput.current_currency.set()


@dp.message_handler(state=DataInput.current_currency)
async def current_reciver(message: types.Message, state: FSMContext):
    """Accepts the current currency and asks for required currency."""
    answer = message.text
    if not REDIS.exists(answer) and answer != 'RUB':
        await message.answer(
            'Нет такой валюты. Выберете текущую валюту',
            reply_markup=currency_button_bar
        )
    else:
        await state.update_data(current=answer)
        await message.answer(
            'Выберете требуемую валюту',
            reply_markup=currency_button_bar
        )
        await DataInput.next()


@dp.message_handler(state=DataInput.required_currency)
async def required_reciver(message: types.Message, state: FSMContext):
    """Accepts the requided currency and asks for amount."""
    answer = message.text
    if not REDIS.exists(answer) and answer != 'RUB':
        await message.answer(
            'Нет такой валюты. Выберете требуемую валюту',
            reply_markup=currency_button_bar
        )
    else:
        await state.update_data(required=answer)
        await message.answer(
            'Введите сумму', reply_markup=ReplyKeyboardRemove()
        )
        await DataInput.next()


@dp.message_handler(state=DataInput.amount_currency)
async def amount_reciver(message: types.Message, state: FSMContext):
    """Accepts the amount of money, returns the result of the calculation."""
    answer = message.text
    await state.update_data(amount=answer)
    data = await state.get_data()
    try:
        result = exchange(
            data['current'].upper(),
            data['required'].upper(),
            float(data['amount'])
        )
    except ValueError:
        await message.answer(
            f'{VALUE_ERR_MESSAGE} Требуется числовое значение.'
        )
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
                await bot.send_photo(
                    message.from_user.id, cat['url'],
                    reply_markup=button_bar
                )


@dp.message_handler(Text('Создать опрос'))
async def create_poll(message: types.Message):
    """Initiates the creation of a survey."""
    await message.answer('Введите вопрос', reply_markup=ReplyKeyboardRemove())
    await DataInput.poll_question.set()


@dp.message_handler(state=DataInput.poll_question)
async def question(message: types.Message, state: FSMContext):
    """Adds question and redirects to next step (add otions for poll)."""
    answer = message.text
    await state.update_data(question=answer)
    await message.answer(
        'Добавьте вариант ответа, или сохраните опрос',
        reply_markup=poll_botton_bar
    )
    await DataInput.next()
    await state.update_data(options=[])


@dp.message_handler(state=DataInput.option)
async def option(message: types.Message, state: FSMContext):
    """Adds option or saves poll."""
    if message.text == 'Сохранить опрос':
        data = await state.get_data()
        if len(data['options']) < MINIMAL_OPTION_AMOUNT:
            await message.answer(
                'Вориантов ответа должно быть больше одного!!!'
            )
            return
        else:
            await message.answer(
                f'Опрос сохранен и отправлен в канал {CHANNEL_URL}',
                reply_markup=button_bar
            )
            await bot.send_message(CHANNEL_ID, 'Пройдите опрос!')
            await bot.send_poll(CHANNEL_ID, data['question'], data['options'])
            await state.finish()
            return
    data = await state.get_data()
    options: list = data['options']
    answer = message.text
    options.append(answer)
    await state.update_data(options=options)
    await message.answer(
        'Добавьте еще вариант ответа, или сохраните опрос',
        reply_markup=poll_botton_bar
    )


@dp.message_handler()
async def use_the_buttons_answer(message: types.Message):
    """Intercepts messages not included in the button pool."""
    await message.answer('Воспользуйтесь кнопками!', reply_markup=button_bar)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
