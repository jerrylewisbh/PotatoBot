from telegram import ReplyKeyboardMarkup, KeyboardButton

from core.commands import ADMIN_COMMAND_ORDER, ADMIN_COMMAND_STATUS, ADMIN_COMMAND_GROUPS, ADMIN_COMMAND_RECRUIT, \
    ADMIN_COMMAND_FIRE_UP, ADMIN_COMMAND_SQUAD_LIST, USER_COMMAND_ME, USER_COMMAND_TOP, USER_COMMAND_SQUAD, \
    USER_COMMAND_STATISTICS, USER_COMMAND_BUILD, USER_COMMAND_CONTACTS, ADMIN_COMMAND_ADMINPANEL,\
    ADMIN_COMMAND_TO_USER_PANEL


def generate_admin_markup(full=False, grp=False):
    buttons = [[KeyboardButton(ADMIN_COMMAND_ORDER)]]
    if full:
        buttons.append([KeyboardButton(ADMIN_COMMAND_STATUS), KeyboardButton(ADMIN_COMMAND_GROUPS)])
    if grp:
        buttons.append([KeyboardButton(ADMIN_COMMAND_RECRUIT), KeyboardButton(ADMIN_COMMAND_FIRE_UP)])
    buttons.append([KeyboardButton(ADMIN_COMMAND_SQUAD_LIST)])
    buttons.append([KeyboardButton(ADMIN_COMMAND_TO_USER_PANEL)])
    return ReplyKeyboardMarkup(buttons, True)


def generate_user_markup(is_admin=False):
    buttons = [[KeyboardButton(USER_COMMAND_ME), KeyboardButton(USER_COMMAND_TOP)],
               [KeyboardButton(USER_COMMAND_SQUAD), KeyboardButton(USER_COMMAND_STATISTICS)],
               [KeyboardButton(USER_COMMAND_BUILD), KeyboardButton(USER_COMMAND_CONTACTS)]]
    if is_admin:
        buttons.append([KeyboardButton(ADMIN_COMMAND_ADMINPANEL)])
    return ReplyKeyboardMarkup(buttons, True)
