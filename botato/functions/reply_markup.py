from telegram import KeyboardButton, ReplyKeyboardMarkup

from core.commands import *
from core.db import Session
from core.model import User

Session()


def generate_admin_markup(full=False):
    buttons = [[KeyboardButton(ADMIN_COMMAND_ORDER)]]
    if full:
        buttons.append([KeyboardButton(ADMIN_COMMAND_STATUS), KeyboardButton(ADMIN_COMMAND_GROUPS)])
    buttons.append([KeyboardButton(ADMIN_COMMAND_SQUAD_LIST)])
    buttons.append([KeyboardButton(USER_COMMAND_BACK)])
    return ReplyKeyboardMarkup(buttons, True)


def generate_user_markup(user_id: int = None):
    """ Create a users keyboard. If user_id is given check if there are settings... """
    user = None
    if user_id:
        user = Session.query(User).filter_by(id=user_id).first()

    buttons = [
        [KeyboardButton(USER_COMMAND_ME), KeyboardButton(USER_COMMAND_TOP)],
        [KeyboardButton(USER_COMMAND_SQUAD), KeyboardButton(USER_COMMAND_STATISTICS)],
    ]

    if user and user.is_squadmember:
        # Squad only features....
        user_menu = [KeyboardButton(USER_COMMAND_EXCHANGE), #KeyboardButton(USER_COMMAND_AUCTION),
                     KeyboardButton(USER_COMMAND_HIDE)]

        # Exchange stuff...
        # STILL IN TESTING

        # Normal squad stuff...
        if not user or not user.api_token:
            # New
            user_menu.append(KeyboardButton(USER_COMMAND_REGISTER))
        elif user.api_token and (not user.is_api_profile_allowed or not user.is_api_stock_allowed):
            # Not complete access...
            user_menu.append(KeyboardButton(USER_COMMAND_REGISTER_CONTINUE))
        elif user.api_token and user.is_api_profile_allowed and user.is_api_stock_allowed:
            # All set up
            user_menu.append(KeyboardButton(USER_COMMAND_SETTINGS))

        buttons.append(user_menu)

    if user and user.admin_permission:
        buttons.append([KeyboardButton(ADMIN_COMMAND_ADMINPANEL)])
    return ReplyKeyboardMarkup(buttons, True)


def generate_top_markup(user: User):
    row1 = [
        KeyboardButton(TOP_COMMAND_GLOBAL),
        KeyboardButton(TOP_COMMAND_CLASS),
    ]
    if user.is_squadmember:
        row1.append(KeyboardButton(TOP_COMMAND_SQUAD))
    row2 = [
        KeyboardButton(USER_COMMAND_BACK)
    ]
    buttons = [row1, row2]

    return ReplyKeyboardMarkup(buttons, True)


def generate_statistics_markup():
    buttons = [
        [
            KeyboardButton(STATISTICS_COMMAND_EXP),
            KeyboardButton(STATISTICS_COMMAND_SKILLS),
            KeyboardButton(STATISTICS_COMMAND_QUESTS),
            KeyboardButton(STATISTICS_COMMAND_FORAY),
        ],  # [
        # KeyboardButton(STATISTICS_COMMAND_QUESTS_ALL),
        # KeyboardButton(STATISTICS_COMMAND_ITEMS_ALL),
        # ],
        [
            KeyboardButton(USER_COMMAND_BACK)
        ]
    ]
    return ReplyKeyboardMarkup(buttons, True)


def generate_squad_markup(is_group_admin=False, in_squad=False):
    buttons = []
    if is_group_admin:
        buttons.append([KeyboardButton(ADMIN_COMMAND_ATTENDANCE), KeyboardButton(ADMIN_COMMAND_REPORTS)])
        buttons.append([KeyboardButton(ADMIN_COMMAND_SQUAD_LIST), KeyboardButton(ADMIN_COMMAND_RECRUIT)])
        buttons.append(
            [
                KeyboardButton(ADMIN_COMMAND_FIRE_UP),
                KeyboardButton(USER_COMMAND_SQUAD_LEAVE),
                KeyboardButton(TOP_COMMAND_SQUAD),
            ]
        )
    elif in_squad:
        buttons = [
            [
                KeyboardButton(USER_COMMAND_SQUAD_LEAVE),
                KeyboardButton(TOP_COMMAND_SQUAD),
            ]
        ]
    else:
        buttons = [[KeyboardButton(USER_COMMAND_SQUAD_REQUEST)]]
    buttons.append([KeyboardButton(USER_COMMAND_BACK)])
    return ReplyKeyboardMarkup(buttons, True)
