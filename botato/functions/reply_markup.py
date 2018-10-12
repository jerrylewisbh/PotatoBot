from telegram import KeyboardButton, ReplyKeyboardMarkup

from core.commands import *
from core.db import Session
from core.model import User

Session()


def generate_admin_markup(full=False):
    buttons = [[KeyboardButton(ADMIN_COMMAND_ORDER)]]
    if full:
        buttons.append([
            KeyboardButton(ADMIN_COMMAND_STATUS),
            KeyboardButton(ADMIN_COMMAND_GROUPS),
            KeyboardButton(ADMIN_COMMAND_SQUAD_LIST)
        ])
        buttons.append([KeyboardButton(ADMIN_COMMAND_SNIPE_LIST)])

    buttons.append([KeyboardButton(USER_COMMAND_BACK)])
    return ReplyKeyboardMarkup(buttons, True)


def generate_user_markup(user_id: int = None):
    """ Create a users keyboard. If user_id is given check if there are settings... """
    user = None
    if user_id:
        user = Session.query(User).filter_by(id=user_id).first()
    buttons = []
    row1 = [
        KeyboardButton(USER_COMMAND_ME), KeyboardButton(USER_COMMAND_TOP), KeyboardButton(USER_COMMAND_STATISTICS)
    ]
    buttons.append(row1)

    if user and user.is_squadmember and user.api_token:
        # Squad only features....
        row2 = [
            KeyboardButton(USER_COMMAND_EXCHANGE),
            KeyboardButton(USER_COMMAND_AUCTION),
            KeyboardButton(USER_COMMAND_HIDE),
            #KeyboardButton(USER_COMMAND_TOOLS)
        ]
        buttons.append(row2)

    row3 = [
        KeyboardButton(USER_COMMAND_SQUAD)
    ]
    if user and user.is_squadmember:
        if not user or not user.api_token:
            # New
            row3.append(KeyboardButton(USER_COMMAND_REGISTER))
        elif user.api_token and (not user.is_api_profile_allowed or not user.is_api_stock_allowed):
            # Not complete access...
            row3.append(KeyboardButton(USER_COMMAND_REGISTER_CONTINUE))
        elif user.api_token and user.is_api_profile_allowed and user.is_api_stock_allowed:
            # All set up
            row3.append(KeyboardButton(USER_COMMAND_SETTINGS))

    if user and user.character and (user.character.guild or user.character.guild_tag):
        row3.append(KeyboardButton(USER_COMMAND_GUILD))


    #row3.append(KeyboardButton(USER_COMMAND_HELP))
    #row3.append(KeyboardButton(USER_COMMAND_TEMP))
    buttons.append(row3)



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
        ],
        [
            KeyboardButton(STATISTICS_COMMAND_FORAY),
            KeyboardButton(STATISTICS_COMMAND_FORAY_GLOBAL),
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
                #KeyboardButton(ADMIN_COMMAND_FIRE_UP),
                KeyboardButton(USER_COMMAND_SQUAD_LEAVE) if in_squad else KeyboardButton(USER_COMMAND_SQUAD_REQUEST),
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
