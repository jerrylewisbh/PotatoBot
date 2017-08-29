from telegram import ReplyKeyboardMarkup, KeyboardButton


def generate_standard_markup():
    buttons = []
    buttons.append([KeyboardButton('Приказы'), KeyboardButton('Статус'), KeyboardButton('Группы')])
    buttons.append([KeyboardButton('Список отряда')])
    return ReplyKeyboardMarkup(buttons, True)


def generate_group_admin_markup():
    buttons = []
    buttons.append([KeyboardButton('Приказы'), KeyboardButton('Заявки в отряд'), KeyboardButton('Список отряда')])
    buttons.append([KeyboardButton('чистка отряда')])
    return ReplyKeyboardMarkup([buttons], True)
