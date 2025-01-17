from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="/info")
    builder.button(text="Список соревнований",  callback_data='competitions')
    builder.button(text="Общая таблица лидеров", callback_data='global_leader_board')
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def cancel_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="Вернуться на главную")
    return builder.as_markup(resize_keyboard=True)