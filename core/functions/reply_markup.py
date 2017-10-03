from telegram import ReplyKeyboardMarkup, KeyboardButton


def generate_admin_markup(full=False, grp=False):
    buttons = [[KeyboardButton('Приказы')]]
    if full:
        buttons.append([KeyboardButton('Статус'), KeyboardButton('Группы')])
    if grp:
        buttons.append([KeyboardButton('Заявки в отряд'), KeyboardButton('Чистка отряда')])
    buttons.append([KeyboardButton('Список отряда')])
    return ReplyKeyboardMarkup(buttons, True)
