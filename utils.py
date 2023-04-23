from aiogram.types import KeyboardButton

from buttons import currency_button_bar
from constants import *


async def add_to_redis(rates: dict):
    REDIS.mset(rates)


def generate_buttons(rates: dict):
    x = 0
    row = []
    for currency in rates.keys():
        x += 1
        button = KeyboardButton(currency)
        row.append(button)
        if len(row) == 11:
            if row not in currency_button_bar['keyboard']:
                currency_button_bar.row(*row)
            row.clear()
        if x == 43:
            row.append('RUB')
            if row not in currency_button_bar['keyboard']:
                currency_button_bar.row(*row)
