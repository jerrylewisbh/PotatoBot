from core.types import Session, User
from functions.profile import send_settings


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
