import os

import aiohttp
import asyncio
from dotenv import load_dotenv

load_dotenv()

city_name = 'сочи'
API_key = os.getenv('WEATHER_API_KEY')
lang = 'ru'

class Weather:
    """Object of weather in the desired city."""
    def __init__(self, data: str) -> None:
        self.data = data
        
    def __str__(self) -> str:
        try:
            self.data['name']
        except KeyError:
            return 'Проверьте правильность ввода города.'
        return (
            f"Город {self.data['name']}:\n"
            f"Сейчас {self.data['weather'][0]['description']}:\n"
            f"Температура сейчас {self.data['main']['temp']} °C\n"
            f"Максимальная сегодня {self.data['main']['temp_max']} °C\n"
            f"Минимальная сегодня {self.data['main']['temp_min']} °C"
        )

async def get_current_weather(city_name):
    async with aiohttp.ClientSession() as session:
        url = 'https://api.openweathermap.org/data/2.5/weather'
        params = {'q': city_name, 'appid': API_key, 'units': 'metric', 'lang': 'ru'}
        async with session.get(url=url, params=params) as response:
            weather_json = await response.json()
            weather = Weather(weather_json)
            return weather



if __name__ == '__main__':
    print(asyncio.run(get_current_weather('сочи')))
