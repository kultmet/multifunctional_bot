import requests

import aiohttp
import asyncio

from constants import *

EXCHANGE_TOKEN = 'XuMYZQlKiNdxh6uEJlAQeHvgKQsZJOlG'

url = 'https://www.cbr-xml-daily.ru/latest.js'

response = requests.get(url)

async def async_exchange():
    fuck = {}
    async with aiohttp.ClientSession() as session:
        url = 'https://www.cbr-xml-daily.ru/latest.js'
        async with session.get(url=url) as response:
            courses_json = await response.json(content_type='application/javascript')
            fuck = courses_json

def check_exception(values, key):
    try:
        values[key]
    except KeyError:
        return KEY_ERR_MESSAGE

def exchange(first_ticket: str, end_ticket: str, amount: float, currency_set):
    
    if first_ticket == BASE_CURRENCY:
        check_exception(currency_set, end_ticket)
        return str(round(amount * currency_set[end_ticket], 2))
    elif end_ticket == BASE_CURRENCY:
        check_exception(currency_set, first_ticket)
        from_cource = 1 / currency_set[first_ticket]
        return str(round(amount * from_cource, 2))
    else:
        check_exception(currency_set, first_ticket)
        check_exception(currency_set, end_ticket)
        from_cource = 1 / currency_set[first_ticket]
        return str(round(amount * from_cource * currency_set[end_ticket], 2))


if __name__ == '__main__':
    print(asyncio.run(async_exchange()))
    print(exchange('USD', 'EUR', 1000))
