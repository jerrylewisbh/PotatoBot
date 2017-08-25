from telegram import ReplyKeyboardMarkup, KeyboardButton


def generate_standard_markup():
    buttons = []
    buttons.append(KeyboardButton('Приказы'))
    buttons.append(KeyboardButton('Статус'))
    buttons.append(KeyboardButton('Группы'))
    return ReplyKeyboardMarkup([buttons], True)
