from telegram import ReplyKeyboardMarkup, KeyboardButton


def generate_standard_markup():
    buttons = []
    buttons.append([KeyboardButton('Приказы'), KeyboardButton('Статус'), KeyboardButton('Группы')])
    buttons.append([KeyboardButton('Список отряда')])
    return ReplyKeyboardMarkup(buttons, True)


def generate_group_admin_markup():
    buttons = []
    buttons.append(KeyboardButton('Приказы'))
    buttons.append(KeyboardButton('Заявки в отряд'))
    buttons.append(KeyboardButton('Список отряда'))
    return ReplyKeyboardMarkup([buttons], True)
