from telegram import ReplyKeyboardMarkup, KeyboardButton
from core.texts import *

def generate_admin_markup(full=False, grp=False):
    buttons = [[KeyboardButton(MSG_ORDER_BUTTON)]]
    if full:
        buttons.append([KeyboardButton(MSG_STATUS_BUTTON), KeyboardButton(MSG_GROUP_BUTTON)])
    if grp:
        buttons.append([KeyboardButton(MSG_CLAIM_BUTTON), KeyboardButton(MSG_CLEAN_BUTTON)])
    buttons.append([KeyboardButton(MSG_SQUAD_LIST_BUTTON)])
    return ReplyKeyboardMarkup(buttons, True)
