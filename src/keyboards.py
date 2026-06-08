from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardRemove

remove_keyboard = ReplyKeyboardRemove()


def kb(*buttons: tuple[str, str]):
    """buttons = [('Текст кнопки', 'callback_data'), ...]"""
    b = InlineKeyboardBuilder()
    for text, data in buttons:
        b.button(text=text, callback_data=data)
    b.adjust(1)
    return b.as_markup()


def url_kb(text: str, url: str):
    b = InlineKeyboardBuilder()
    b.button(text=text, url=url)
    return b.as_markup()


def booking_keyboard(url: str):
    return url_kb("📅 Записаться на созвон", url)
