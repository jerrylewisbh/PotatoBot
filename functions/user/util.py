import json
import logging

from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup

from core.handler.callback.util import create_callback, CallbackAction
from core.texts import *
from core.types import Session, User, UserExchangeOrder, UserStockHideSetting, Admin, Group
from functions.user import __delete_group_admin


def __toggle_sniping(bot, update, user):
    user.setting_automated_sniping = not user.setting_automated_sniping
    Session.add(user)
    Session.commit()
    send_settings(bot, update, user)


def __toggle_gold_hiding(bot, update, user):
    user.setting_automated_hiding = not user.setting_automated_hiding
    Session.add(user)
    Session.commit()
    send_settings(bot, update, user)


def __toggle_deal_report(bot, update, user):
    user.setting_automated_deal_report = not user.setting_automated_deal_report
    Session.add(user)
    Session.commit()
    send_settings(bot, update, user)


def __toggle_report(bot, update, user):
    user.setting_automated_report = not user.setting_automated_report
    Session.add(user)
    Session.commit()
    send_settings(bot, update, user)


def __disable_api(bot, update, user):
    if user.api_token:
        user.api_token = None

        user.is_api_profile_allowed = False
        user.is_api_stock_allowed = False
        user.is_api_trade_allowed = False

        user.api_request_id = None
        user.api_grant_operation = None

        # TODO: Do we need to reset settings?

        Session.add(user)
        Session.commit()
    send_settings(bot, update, user)


def disable_api_functions(user):
    logging.info("Disabling API functions for user_id='%s'", user.id)
    # Disable API settings but keep his api credentials until user revokes them herself/himself.
    user.setting_automated_sniping = False
    user.setting_automated_hiding = False
    user.setting_automated_report = False
    user.setting_automated_deal_report = False
    # Remove all his settings...
    Session.query(UserExchangeOrder).filter(UserExchangeOrder.user_id == user.id).delete()
    Session.query(UserStockHideSetting).filter(UserStockHideSetting.user_id == user.id).delete()
    Session.add(user)
    Session.commit()


def send_settings(bot, update, user):
    automated_report = MSG_NEEDS_API_ACCESS
    if user.api_token and user.is_api_profile_allowed:
        automated_report = user.setting_automated_report

    automated_deal_report = MSG_NEEDS_API_ACCESS
    if user.api_token and user.is_api_stock_allowed:
        automated_deal_report = user.setting_automated_deal_report

    automated_sniping = MSG_NEEDS_TRADE_ACCESS
    if user.api_token and user.is_api_trade_allowed:
        automated_sniping = user.setting_automated_sniping

    automated_hiding = MSG_NEEDS_TRADE_ACCESS
    if user.api_token and user.is_api_trade_allowed:
        automated_hiding = user.setting_automated_hiding

    msg = MSG_SETTINGS_INFO.format(
        automated_report,
        automated_deal_report,
        automated_sniping,
        automated_hiding,
        user.stock.date if user.stock else "Unknown",
        user.character.date if user.character else "Unknown",
    )

    if update.callback_query:
        bot.editMessageText(
            text=msg,
            chat_id=user.id,
            message_id=update.callback_query.message.message_id,
            reply_markup=__generate_settings_keyboard(user),
            parse_mode=ParseMode.HTML
        )
    else:
        bot.send_message(
            text=msg,
            chat_id=user.id,
            reply_markup=__generate_settings_keyboard(user),
            parse_mode=ParseMode.HTML
        )


def __generate_settings_keyboard(user, back_key=False):
    inline_keys = []
    if user.api_token:
        inline_keys.append(
            [
                InlineKeyboardButton(BTN_SETTING_API_DISABLE, callback_data=create_callback(
                    CallbackAction.SETTING,
                    user.id,
                    setting_action="disable_api",
                ))
            ]
        )
    if user.is_squadmember and user.is_api_stock_allowed and user.is_api_profile_allowed and user.api_token:
        if user.setting_automated_report:
            inline_keys.append(
                [
                    InlineKeyboardButton(BTN_SETTING_DISABLE_REPORT, callback_data=create_callback(
                        CallbackAction.SETTING,
                        user.id,
                        setting_action="report",
                    ))
                ]
            )
        else:
            inline_keys.append(
                [
                    InlineKeyboardButton(BTN_SETTING_ENABLE_REPORT, callback_data=create_callback(
                        CallbackAction.SETTING,
                        user.id,
                        setting_action="report",
                    ))
                ]
            )
        if user.setting_automated_deal_report:
            inline_keys.append(
                [
                    InlineKeyboardButton(BTN_SETTING_DISABLE_DEAL_REPORT, callback_data=create_callback(
                        CallbackAction.SETTING,
                        user.id,
                        setting_action="deal_report",
                    ))
                ]
            )
        else:
            inline_keys.append(
                [
                    InlineKeyboardButton(BTN_SETTING_ENABLE_DEAL_REPORT, callback_data=create_callback(
                        CallbackAction.SETTING,
                        user.id,
                        setting_action="deal_report",
                    ))
                ]
            )
    if user.is_squadmember and user.is_api_trade_allowed and user.api_token:
        if user.setting_automated_sniping:
            inline_keys.append(
                [
                    InlineKeyboardButton(BTN_SETTING_DISABLE_SNIPING, callback_data=create_callback(
                        CallbackAction.SETTING,
                        user.id,
                        setting_action="sniping",
                    ))
                ]
            )
        else:
            inline_keys.append(
                [
                    InlineKeyboardButton(BTN_SETTING_ENABLE_SNIPING, callback_data=create_callback(
                        CallbackAction.SETTING,
                        user.id,
                        setting_action="sniping",
                    ))
                ]
            )
    if user.is_squadmember and user.is_api_trade_allowed and user.api_token:
        if user.setting_automated_hiding:
            inline_keys.append(
                [
                    InlineKeyboardButton(BTN_SETTING_DISABLE_HIDE_GOLD, callback_data=create_callback(
                        CallbackAction.SETTING,
                        user.id,
                        setting_action="hiding",
                    ))
                ]
            )
        else:
            inline_keys.append(
                [
                    InlineKeyboardButton(BTN_SETTING_ENABLE_HIDE_GOLD, callback_data=create_callback(
                        CallbackAction.SETTING,
                        user.id,
                        setting_action="hiding",
                    ))
                ]
            )
    if inline_keys:
        return InlineKeyboardMarkup(inline_keys)
    return None
