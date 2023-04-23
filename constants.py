import os

from dotenv import load_dotenv
import redis

load_dotenv()


REDIS = redis.Redis(host='localhost', port=6379, decode_responses=True)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
API_WEATHER = os.getenv('WEATHER_API_KEY')

CHANNEL_URL = 'https://t.me/kazback_bot_reciver'
CHANNEL_ID = '@kazback_bot_reciver'
BASE_CURRENCY = 'RUB'
INVATION = (
        'Формат принимаемых данных:\n'
        'валюты принимаются в формете тикетов, напр: USD, EUR\n'
        '<исходная валюта*> <требуемая валюта> <колличество>\n'
        'Например: "USD EUR 1000"\n'
        'Ведите параметры конвертаци...'
    )

KEY_ERR_MESSAGE = 'Что-то пошло не так!'
VALUE_ERR_MESSAGE = 'Проверьте формат ввода!'

WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'
WEATHER_PARAMS = {
                'q': None,
                'appid': API_WEATHER,
                'units': 'metric',
                'lang': 'ru'
            }
CATS_URL = 'https://api.thecatapi.com/v1/images/search'
CURRENCY_URL = 'https://www.cbr-xml-daily.ru/latest.js'


