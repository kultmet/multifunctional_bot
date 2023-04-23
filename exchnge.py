import requests

import aiohttp
import asyncio

from constants import *

url = 'https://www.cbr-xml-daily.ru/latest.js'

response = requests.get(url)


async def async_exchange():
    async with aiohttp.ClientSession() as session:
        url = 'https://www.cbr-xml-daily.ru/latest.js'
        async with session.get(url=url) as response:
            courses_json = await response.json(
                content_type='application/javascript'
            )
            print(courses_json)


def exchange(first_ticket: str, end_ticket: str, amount: float):
    if first_ticket == end_ticket:
        return 'Если вы хотите получить результаты, выбирайте разные валюты.'
    if first_ticket == BASE_CURRENCY:
        return str(round(amount * float(REDIS.get(end_ticket)), 2))
    elif end_ticket == BASE_CURRENCY:
        from_cource = 1 / float(REDIS.get(first_ticket))
        return str(round(amount * from_cource, 2))
    else:
        from_cource = 1 / float(REDIS.get(first_ticket))
        return str(
            round(amount * from_cource * float(REDIS.get(end_ticket)), 2)
        )


if __name__ == '__main__':
    asyncio.run(async_exchange())
    print(exchange('USD', 'EUR', 1000))
