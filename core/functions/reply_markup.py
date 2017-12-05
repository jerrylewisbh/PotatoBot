from telegram import ReplyKeyboardMarkup, KeyboardButton

from core.commands import ADMIN_COMMAND_ORDER, ADMIN_COMMAND_STATUS, ADMIN_COMMAND_GROUPS, ADMIN_COMMAND_RECRUIT, \
    ADMIN_COMMAND_FIRE_UP, ADMIN_COMMAND_SQUAD_LIST, USER_COMMAND_ME, USER_COMMAND_TOP, USER_COMMAND_SQUAD, \
    USER_COMMAND_STATISTICS, USER_COMMAND_BUILD, USER_COMMAND_CONTACTS, ADMIN_COMMAND_ADMINPANEL, \
    USER_COMMAND_SQUAD_REQUEST, USER_COMMAND_BACK, TOP_COMMAND_ATTACK, TOP_COMMAND_DEFENCE, TOP_COMMAND_EXP, \
    STATISTICS_COMMAND_EXP, USER_COMMAND_SQUAD_LEAVE, ADMIN_COMMAND_REPORTS, TOP_COMMAND_GLOBAL_BUILD, \
    TOP_COMMAND_WEEK_BUILD, TOP_COMMAND_WEEK_BATTLES


def generate_admin_markup(full=False):
    buttons = [[KeyboardButton(ADMIN_COMMAND_ORDER)]]
    if full:
        buttons.append([KeyboardButton(ADMIN_COMMAND_STATUS), KeyboardButton(ADMIN_COMMAND_GROUPS)])
    buttons.append([KeyboardButton(ADMIN_COMMAND_SQUAD_LIST)])
    buttons.append([KeyboardButton(USER_COMMAND_BACK)])
    return ReplyKeyboardMarkup(buttons, True)


def generate_user_markup(is_admin=False):
    buttons = [[KeyboardButton(USER_COMMAND_ME), KeyboardButton(USER_COMMAND_TOP)],
               [KeyboardButton(USER_COMMAND_SQUAD), KeyboardButton(USER_COMMAND_STATISTICS)],
               [KeyboardButton(USER_COMMAND_BUILD), KeyboardButton(USER_COMMAND_CONTACTS)]]
    if is_admin:
        buttons.append([KeyboardButton(ADMIN_COMMAND_ADMINPANEL)])
    return ReplyKeyboardMarkup(buttons, True)


def generate_top_markup():
    buttons = [[KeyboardButton(TOP_COMMAND_ATTACK), KeyboardButton(TOP_COMMAND_DEFENCE),
                KeyboardButton(TOP_COMMAND_EXP), KeyboardButton(TOP_COMMAND_GLOBAL_BUILD)],
               [KeyboardButton(TOP_COMMAND_WEEK_BUILD), KeyboardButton(TOP_COMMAND_WEEK_BATTLES)],
               [KeyboardButton(USER_COMMAND_BACK)]]
    return ReplyKeyboardMarkup(buttons, True)


def generate_statistics_markup():
    buttons = [[KeyboardButton(STATISTICS_COMMAND_EXP)],
               [KeyboardButton(USER_COMMAND_BACK)]]
    return ReplyKeyboardMarkup(buttons, True)


def generate_squad_markup(is_group_admin=False, in_squad=False):
    if in_squad:
        buttons = [[KeyboardButton(USER_COMMAND_SQUAD_LEAVE)]]
    else:
        buttons = [[KeyboardButton(USER_COMMAND_SQUAD_REQUEST)]]
    if is_group_admin:
        buttons.append([KeyboardButton(ADMIN_COMMAND_REPORTS), KeyboardButton(ADMIN_COMMAND_RECRUIT)])
        buttons.append([KeyboardButton(ADMIN_COMMAND_SQUAD_LIST), KeyboardButton(ADMIN_COMMAND_FIRE_UP)])
    buttons.append([KeyboardButton(USER_COMMAND_BACK)])
    return ReplyKeyboardMarkup(buttons, True)
