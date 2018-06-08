from telegram import KeyboardButton, ReplyKeyboardMarkup

from core.commands import (ADMIN_COMMAND_ADMINPANEL, ADMIN_COMMAND_ATTENDANCE,
                           ADMIN_COMMAND_FIRE_UP, ADMIN_COMMAND_GROUPS,
                           ADMIN_COMMAND_ORDER, ADMIN_COMMAND_RECRUIT,
                           ADMIN_COMMAND_REPORTS, ADMIN_COMMAND_SQUAD_LIST,
                           ADMIN_COMMAND_STATUS, STATISTICS_COMMAND_EXP,
                           STATISTICS_COMMAND_SKILLS, TOP_COMMAND_ATTACK,
                           TOP_COMMAND_BATTLES, TOP_COMMAND_DEFENCE, TOP_COMMAND_EXP,
                           USER_COMMAND_BACK, USER_COMMAND_ME,
                           USER_COMMAND_REGISTER,
                           USER_COMMAND_REGISTER_CONTINUE,
                           USER_COMMAND_SETTINGS, USER_COMMAND_SQUAD,
                           USER_COMMAND_SQUAD_LEAVE,
                           USER_COMMAND_SQUAD_REQUEST, USER_COMMAND_STATISTICS,
                           USER_COMMAND_TOP, USER_COMMAND_EXCHANGE)
from core.types import Session, User

Session()

def generate_admin_markup(full=False):
    buttons = [[KeyboardButton(ADMIN_COMMAND_ORDER)]]
    if full:
        buttons.append([KeyboardButton(ADMIN_COMMAND_STATUS), KeyboardButton(ADMIN_COMMAND_GROUPS)])
    buttons.append([KeyboardButton(ADMIN_COMMAND_SQUAD_LIST)])
    buttons.append([KeyboardButton(USER_COMMAND_BACK)])
    return ReplyKeyboardMarkup(buttons, True)


def generate_user_markup(user_id=None):
    """ Create a users keyboard. If user_id is given check if there are settings... """
    user = None
    if user_id:
        user = Session.query(User).filter_by(id=user_id).first()

    buttons = [
        [KeyboardButton(USER_COMMAND_ME), KeyboardButton(USER_COMMAND_TOP)],
        [KeyboardButton(USER_COMMAND_SQUAD), KeyboardButton(USER_COMMAND_STATISTICS)],
        #[KeyboardButton(USER_COMMAND_BUILD), KeyboardButton(USER_COMMAND_CONTACTS)]
    ]

    if user and user.is_squadmember:
        # Squad only features....
        user_menu = []

        # Exchange stuff...
        # STILL IN TESTING
        if user.api_token and user.is_api_profile_allowed and user.is_tester:
            #user_menu.append(KeyboardButton(USER_COMMAND_HIDE))
            user_menu.append(KeyboardButton(USER_COMMAND_EXCHANGE))

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


def generate_top_markup():
    buttons = [[KeyboardButton(TOP_COMMAND_ATTACK), KeyboardButton(TOP_COMMAND_DEFENCE),
                KeyboardButton(TOP_COMMAND_EXP),
                # KeyboardButton(TOP_COMMAND_BUILD),
                KeyboardButton(TOP_COMMAND_BATTLES)],
               [KeyboardButton(USER_COMMAND_BACK)]]
    return ReplyKeyboardMarkup(buttons, True)


def generate_statistics_markup():
    buttons = [[KeyboardButton(STATISTICS_COMMAND_EXP), KeyboardButton(STATISTICS_COMMAND_SKILLS)],
               [KeyboardButton(USER_COMMAND_BACK)]]
    return ReplyKeyboardMarkup(buttons, True)


def generate_squad_markup(is_group_admin=False, in_squad=False):
    buttons = []
    if is_group_admin:
        buttons.append([KeyboardButton(ADMIN_COMMAND_ATTENDANCE), KeyboardButton(ADMIN_COMMAND_REPORTS)])
        buttons.append([KeyboardButton(ADMIN_COMMAND_SQUAD_LIST), KeyboardButton(ADMIN_COMMAND_RECRUIT)])
        buttons.append([KeyboardButton(ADMIN_COMMAND_FIRE_UP), KeyboardButton(USER_COMMAND_SQUAD_LEAVE)])
    elif in_squad:
        buttons = [[KeyboardButton(USER_COMMAND_SQUAD_LEAVE)]]
    else:
        buttons = [[KeyboardButton(USER_COMMAND_SQUAD_REQUEST)]]
    buttons.append([KeyboardButton(USER_COMMAND_BACK)])
    return ReplyKeyboardMarkup(buttons, True)
