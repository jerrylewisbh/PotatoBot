import logging

import telegram
from telegram import ParseMode

from core.texts import MSG_NEEDS_API_ACCESS, MSG_NEEDS_TRADE_ACCESS, MSG_SETTINGS_INFO
from core.types import Session, User, UserExchangeOrder, UserStockHideSetting
from functions.inline_markup import generate_settings_buttons


def toggle_sniping(bot, update, user, data):
    user = Session.query(User).filter_by(id=data['id']).first()
    if user.setting_automated_sniping:
        user.setting_automated_sniping = False
    else:
        user.setting_automated_sniping = True
    Session.add(user)
    Session.commit()
    send_settings(bot, update, user)


def toggle_gold_hiding(bot, update, user, data):
    user = Session.query(User).filter_by(id=data['id']).first()
    if user.setting_automated_hiding:
        user.setting_automated_hiding = False
    else:
        user.setting_automated_hiding = True
    Session.add(user)
    Session.commit()
    send_settings(bot, update, user)


def toggle_deal_report(bot, update, user, data):
    user = Session.query(User).filter_by(id=data['id']).first()
    if user.setting_automated_deal_report:
        user.setting_automated_deal_report = False
    else:
        user.setting_automated_deal_report = True
    Session.add(user)
    Session.commit()
    send_settings(bot, update, user)


def toggle_report(bot, update, user, data):
    user = Session.query(User).filter_by(id=data['id']).first()
    if user.setting_automated_report:
        user.setting_automated_report = False
    else:
        user.setting_automated_report = True
    Session.add(user)
    Session.commit()
    send_settings(bot, update, user)


def disable_api(bot, update, user, data):
    user = Session.query(User).filter_by(id=data['id']).first()
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


def create_or_update_user(telegram_user: telegram.User) -> User:
    """

    :type telegram_user: object
    :rtype: User
    """
    if not telegram_user:
        return None
    user = Session.query(User).filter_by(id=telegram_user.id).first()
    if not user:
        user = User(
            id=telegram_user.id,
            username=telegram_user.username or '',
            first_name=telegram_user.first_name or '',
            last_name=telegram_user.last_name or ''
        )
        Session.add(user)
    else:
        updated = False
        if user.username != telegram_user.username:
            user.username = telegram_user.username
            updated = True
        if user.first_name != telegram_user.first_name:
            user.first_name = telegram_user.first_name
            updated = True
        if user.last_name != telegram_user.last_name:
            user.last_name = telegram_user.last_name
            updated = True
        if updated:
            Session.add(user)
    Session.commit()
    return user


def send_settings(bot, update, user):
    automated_report = MSG_NEEDS_API_ACCESS
    if user.api_token and user.is_api_profile_allowed:
        automated_report = user.setting_automated_report

    automated_deal_report = MSG_NEEDS_API_ACCESS
    if user.api_token and user.is_api_stock_allowed:
        automated_deal_report = user.setting_automated_deal_report

    automated_sniping = MSG_NEEDS_TRADE_ACCESS
    if user.api_token and user.is_api_trade_allowed:
        automated_sniping =  user.setting_automated_sniping

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
            reply_markup=generate_settings_buttons(user),
            parse_mode=ParseMode.HTML
        )
    else:
        bot.send_message(
            text=msg,
            chat_id=user.id,
            reply_markup=generate_settings_buttons(user),
            parse_mode=ParseMode.HTML
        )
