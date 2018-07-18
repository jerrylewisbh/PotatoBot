import logging
from html import escape

import redis
from datetime import datetime, timedelta
from enum import Enum
from pymysql import IntegrityError
from sqlalchemy import func, collate
from sqlalchemy.exc import SQLAlchemyError
from telegram import ParseMode, Update, TelegramError
from telegram.error import Unauthorized, BadRequest, TimedOut, NetworkError, ChatMigrated

from config import CWBOT_ID, REDIS_SERVER, REDIS_PORT, LOG_ALLOWED_RECIPIENTS, LOGFILE
from core.bot import MQBot
from core.decorators import command_handler
from core.state import GameState, get_game_state
from core.texts import *
from core.db import Session, new_item
from core.enums import AdminType
from core.model import Group, User, Admin, Stock, Squad, SquadMember, Ban, Item
from core.utils import send_async
from functions.reply_markup import (generate_admin_markup)
from functions.user.util import disable_api_functions

Session()


class StockType(Enum):
    Stock = 0
    TradeBot = 1


def error_callback(bot: MQBot, update, error, **kwargs):
    """ Error handling """
    try:
        raise error
    except Unauthorized:
        if update.message.chat_id:
            # Group?
            group = Session.query(Group).filter(Group.id == update.message.chat_id).first()
            if group is not None:
                group.bot_in_group = False
                Session.add(group)
                Session.commit()

            # remove update.message.chat_id from conversation list
            user = Session.query(User).filter(User.id == update.message.chat_id).first()
            if user:
                logging.info(
                    "Unauthorized for user_id='%s'. Disabling API settings so that we don't contact the user in the future",
                    user.id)
                disable_api_functions(user)
            else:
                logging.warning(
                    "Unauthorized occurred: %s. We should probably remove user chat_id='%s' from bot.",
                    error.message,
                    update.message.chat_id,
                    exc_info=True
                )
    except BadRequest:
        # handle malformed requests - read more below!
        logging.error("BadRequest occurred: %s", error.message, exc_info=True)
    except TimedOut:
        # handle slow connection problems
        logging.error("TimedOut occurred: %s", error.message, exc_info=True)
    except NetworkError:
        # handle other connection problems

        logging.error("NetworkError occurred: %s", error.message, exc_info=True)
    except ChatMigrated as e:
        # the chat_id of a group has changed, use e.new_chat_id instead
        logging.warning(
            "ChatMigrated occurred: %s",
            error.message,
            exc_info=True
        )
    except TelegramError:
        # handle all other telegram related errors
        logging.error("TelegramError occurred: %s", error.message, exc_info=True)
    except Exception:
        print("START ##################################################")
        print(error)
        print("END ####################################################")


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=True
)
def admin_panel(bot: MQBot, update: Update, user: User):
    if update.message.chat.type == 'private':
        admin = Session.query(Admin).filter_by(user_id=update.message.from_user.id).all()
        full_adm = False
        for adm in admin:
            if adm.admin_type <= AdminType.FULL.value:
                full_adm = True
        send_async(bot, chat_id=update.message.chat.id, text=MSG_ADMIN_WELCOME,
                   reply_markup=generate_admin_markup(full_adm))


@command_handler(
    min_permission=AdminType.FULL,
    allow_private=False,
    allow_group=True
)
def force_kick_botato(bot: MQBot, update: Update, user: User):
    bot.leave_chat(update.message.chat.id)


@command_handler()
def help_msg(bot: MQBot, update, user: User):
    admin_user = Session.query(Admin).filter_by(user_id=update.message.from_user.id).all()
    global_adm = False
    for adm in admin_user:
        if adm.admin_type <= AdminType.FULL.value:
            global_adm = True
            break
    if global_adm:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_HELP_GLOBAL_ADMIN, parse_mode=ParseMode.HTML)
    elif len(admin_user) != 0:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_HELP_GROUP_ADMIN, parse_mode=ParseMode.HTML)
    else:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_HELP_USER, parse_mode=ParseMode.HTML)


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=True,
    allow_group=True
)
def ping(bot: MQBot, update: Update, user: User):
    send_date = update.effective_message.date
    ping_time = send_date - datetime.now()

    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=MSG_PING.format(update.message.from_user.username, (ping_time.microseconds / 1000)),
        parse_mode=ParseMode.MARKDOWN,
    )


def get_diff(dict_one, dict_two):
    resource_diff_add = {}
    resource_diff_del = {}
    for key, val in dict_one.items():
        if key in dict_two:
            diff_count = dict_one[key] - dict_two[key]
            if diff_count > 0:
                resource_diff_add[key] = diff_count
            elif diff_count < 0:
                resource_diff_del[key] = diff_count
        else:
            resource_diff_add[key] = val
    for key, val in dict_two.items():
        if key not in dict_one:
            resource_diff_del[key] = -val
    resource_diff_add = sorted(resource_diff_add.items(), key=lambda x: x[0])
    resource_diff_del = sorted(resource_diff_del.items(), key=lambda x: x[0])
    return resource_diff_add, resource_diff_del


def get_weight_multiplier(item_name):
    item = __get_item(item_name)
    if not item:
        new_item(item_name, False)
        return 1

    return item.weight


def get_weighted_diff(dict_one, dict_two):
    """ Same as get_diff but accounts for item weight """
    resource_diff_add = {}
    resource_diff_del = {}

    for key, val in dict_one.items():
        weight_multiplier = get_weight_multiplier(key)
        if key in dict_two:
            diff_count = dict_one[key] - dict_two[key]
            if diff_count > 0:
                resource_diff_add[key] = diff_count * weight_multiplier
            elif diff_count < 0:
                resource_diff_del[key] = diff_count * weight_multiplier
        else:
            resource_diff_add[key] = val * weight_multiplier
    for key, val in dict_two.items():
        weight_multiplier = get_weight_multiplier(key)
        if key not in dict_one:
            resource_diff_del[key] = -val * weight_multiplier
    resource_diff_add = sorted(resource_diff_add.items(), key=lambda x: x[0])
    resource_diff_del = sorted(resource_diff_del.items(), key=lambda x: x[0])
    return resource_diff_add, resource_diff_del


def stock_split(old_stock, new_stock):
    """ Split stock text... """
    resources_old = {}
    resources_new = {}
    strings = old_stock.splitlines()
    for string in strings[1:]:
        resource = string.split(' (')
        resource[1] = resource[1][:-1]
        resources_old[resource[0]] = int(resource[1])
    strings = new_stock.splitlines()
    for string in strings[1:]:
        resource = string.split(' (')
        resource[1] = resource[1][:-1]
        resources_new[resource[0]] = int(resource[1])

    return resources_old, resources_new


def __get_item(item_name):
    return Session.query(Item).filter(
        Item.name == collate(item_name, 'utf8mb4_unicode_520_ci')
    ).first()


def stock_compare_text(old_stock, new_stock):
    """ Compare stock... """
    if old_stock:
        resources_old, resources_new = stock_split(old_stock, new_stock)
        resource_diff_add, resource_diff_del = get_diff(resources_new, resources_old)
        msg = MSG_STOCK_COMPARE_HARVESTED
        hits = 0
        running_total = 0
        if len(resource_diff_add):
            for key, val in resource_diff_add:
                item = __get_item(key)
                if item and item.pillagable:
                    gain_worth = __get_item_worth(item.name)
                    hits += 1
                    if item.tradable and gain_worth:
                        running_total += (gain_worth * val)
                        msg += MSG_STOCK_COMPARE_W_PRICE.format(key, val, gain_worth, (gain_worth * val))
                    else:
                        msg += MSG_STOCK_COMPARE_WO_PRICE.format(key, val)
        if hits == 0:
            msg += MSG_EMPTY

        msg += MSG_STOCK_COMPARE_LOST
        hits = 0
        if len(resource_diff_del):
            for key, val in resource_diff_del:
                item = __get_item(key)
                if item and item.pillagable:
                    hits += 1
                    loss_worth = __get_item_worth(item.name)
                    if item.tradable and loss_worth:
                        running_total += (loss_worth * val)
                        msg += MSG_STOCK_COMPARE_W_PRICE.format(key, val, loss_worth, (loss_worth * val))
                    else:
                        msg += MSG_STOCK_COMPARE_WO_PRICE.format(key, val)
        if hits == 0:
            msg += MSG_EMPTY

        if running_total != 0:
            msg += MSG_STOCK_OVERALL_CHANGE.format(running_total)

        return msg

    return None


def stock_compare(user_id, new_stock_text):
    """ Save new stock into database and compare it with the newest already saved.
    """

    old_stock = Session.query(Stock).filter_by(user_id=user_id,
                                               stock_type=StockType.Stock.value).order_by(Stock.date.desc()).first()
    new_stock = Stock()
    new_stock.stock = new_stock_text
    new_stock.stock_type = StockType.Stock.value
    new_stock.user_id = user_id
    new_stock.date = datetime.now()
    Session.add(new_stock)
    Session.commit()

    if old_stock:
        return stock_compare_text(old_stock.stock, new_stock.stock)

    return None


@command_handler(
    forward_from=CWBOT_ID
)
def stock_compare_forwarded(bot: MQBot, update: Update, user: User, chat_data: dict):
    # If user-stock is automatically updated via API do not allow reports during SILENCE
    user = Session.query(User).filter_by(id=update.message.from_user.id).first()

    state = get_game_state()
    if user.is_api_stock_allowed and user.setting_automated_report and GameState.NO_REPORTS in state:
        text = MSG_NO_REPORT_PHASE_BEFORE_BATTLE if GameState.NIGHT in state else MSG_NO_REPORT_PHASE_AFTER_BATTLE
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=text,
            parse_mode=ParseMode.HTML)
        return

    cmp_result = stock_compare(update.message.from_user.id, update.message.text)
    if cmp_result:
        send_async(bot, chat_id=update.message.chat.id, text=cmp_result, parse_mode=ParseMode.HTML)
    else:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_STOCK_COMPARE_WAIT, parse_mode=ParseMode.HTML)


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def delete_msg(bot: MQBot, update: Update, user: User):
    bot.delete_message(update.message.reply_to_message.chat_id, update.message.reply_to_message.message_id)
    bot.delete_message(update.message.reply_to_message.chat_id, update.message.message_id)


@command_handler(
    min_permission=AdminType.FULL,
    allow_private=False,
    allow_group=True
)
def kick_from_chat(bot: MQBot, update: Update, user: User):
    bot.kickChatMember(update.message.reply_to_message.chat_id, update.message.reply_to_message.from_user.id)
    bot.unbanChatMember(update.message.reply_to_message.chat_id, update.message.reply_to_message.from_user.id)


@command_handler(
    min_permission=AdminType.FULL,
)
def ban(bot: MQBot, update: Update, user: User):
    """ Ban Command """

    try:
        username, reason = update.message.text.split(' ', 2)[1:]
    except ValueError:
        send_async(
            bot,
            chat_id=update.message.chat_id,
            text="Missing parameters. Format is /ban @username <some reason> or /ban userid <some reason>!"
        )
        return

    username = username.replace('@', '')
    ban_user = Session.query(User).filter_by(username=username).first()
    if not ban_user:
        try:
            # If we found no match, try to find by user_Id
            ban_user = Session.query(User).filter(User.id == int(username)).first()
        except ValueError:
            pass

    if ban_user:
        # Compare permissions between ban user and user who requests it. Only if they are not equal we allow that!
        max_permission_requester = AdminType.NOT_ADMIN
        for permission in user.permissions:
            if permission.admin_type < max_permission_requester:
                max_permission_requester = permission.admin_type

        max_permission_ban_user = AdminType.NOT_ADMIN
        for permission in ban_user.permissions:
            if permission.admin_type < max_permission_ban_user:
                max_permission_ban_user = permission.admin_type

        # Requester has HIGHER rights...
        if max_permission_requester >= max_permission_ban_user:
            logging.warning(
                "[Ban] user_id='%s' tried to ban user_id='%s' but he has same or higher privileges",
                user.id,
                ban_user.id
            )
            send_async(
                bot,
                chat_id=update.message.chat_id,
                text="🚨 Not a chance! Find someone with higher permissions."
            )
            return
        else:
            banned = Session.query(Ban).filter_by(user_id=ban_user.id).first()
            if banned:
                logging.info("[Ban] user_id='%s' is already banned", ban_user.id)
                send_async(
                    bot,
                    chat_id=update.message.chat.id,
                    text=MSG_ALREADY_BANNED
                )
            else:
                was_banned = __ban(bot, ban_user, reason)
                if was_banned:
                    send_async(
                        bot,
                        chat_id=update.message.chat.id,
                        text=MSG_BAN_COMPLETE
                    )
                    try:
                        send_async(
                            bot,
                            chat_id=update.message.chat_id,
                            text=__get_user_info(bot, ban_user),
                            parse_mode=ParseMode.HTML,
                        )
                    # This might fail due to channels botato was removed from that where previously unknown...
                    except TelegramError:
                        send_async(
                            bot,
                            chat_id=update.message.chat_id,
                            parse_mode=ParseMode.HTML,
                            text="Something went wrong generating the report. Try again. If it still fails notify admins!"
                        )
                else:
                    send_async(
                        bot,
                        chat_id=update.message.chat.id,
                        text="Ban failed? Check logs!"
                    )
    else:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_USER_UNKNOWN)

@command_handler(
    min_permission=AdminType.FULL,
)
def user_info(bot: MQBot, update: Update, user: User):
    """ Check one ban """

    username = update.message.text.split(' ', 1)[1]
    username = username.replace('@', '')
    ban_user = Session.query(User).filter_by(username=username).first()
    if not ban_user:
        try:
            # If we found no match, try to find by user_Id
            ban_user = Session.query(User).filter(User.id == int(username)).first()
        except ValueError:
            pass

    if not ban_user:
        # Compare permissions between ban user and user who requests it. Only if they are not equal we allow that!
        send_async(
            bot,
            chat_id=update.message.chat_id,
            text="User is not banned or unknown!"
        )
    else:
        try:
            send_async(
                bot,
                chat_id=update.message.chat_id,
                text=__get_user_info(bot, ban_user),
                parse_mode=ParseMode.HTML,
            )
        # This might fail due to channels botato was removed from that where previously unknown...
        except TelegramError:
            send_async(
                bot,
                chat_id=update.message.chat_id,
                parse_mode=ParseMode.HTML,
                text="Something went wrong generating the report. Try again. If it still fails notify admins!"
            )
@command_handler(
    min_permission=AdminType.FULL,
)
def ban_info_all(bot: MQBot, update: Update, user: User):
    """ Check all bans """

    all_banned = Session.query(Ban).all()
    for ban in all_banned:
        ban_user = ban.user
        try:
            send_async(
                bot,
                chat_id=update.message.chat_id,
                text=__get_user_info(bot, ban_user),
                parse_mode=ParseMode.HTML,
            )
        # This might fail due to channels botato was removed from that where previously unknown...
        except TelegramError:
            send_async(
                bot,
                chat_id=update.message.chat_id,
                parse_mode=ParseMode.HTML,
                text="Something went wrong generating the report. Try again. If it still fails notify admins!"
            )

def __get_user_info(bot: MQBot, ban_user: User):
    text = "<b>User:</b> {}\n<b>Status:</b> {}\n\n".format(
        "@"+escape(ban_user.username) if ban_user.username else ban_user.id,
        "⚱️BANNED" if ban_user.is_banned else "👌 Not banned"
    )

    text += "<b>Status in all ACTIVE chats:</b>\n"

    all_active_groups = Session.query(Group).filter(
        Group.bot_in_group == True
    ).all()
    for group in all_active_groups:
        chat_user_banned = bot.get_chat_member(group.id, ban_user.id)

        status = "❓ Unknown"
        if ban_user.is_banned:
            if chat_user_banned.status == 'kicked':
                status = "✅Banned"
            elif chat_user_banned.status == 'left':
                status = "⚠️Not in group but not banned! (Missing Bot-Permissions?)"
            elif chat_user_banned.status == 'restricted':
                status = "⚠️Restricted but not banned!"
            elif chat_user_banned.status == 'member':
                status = "🚨In group (unbanned!)"
            elif chat_user_banned.status == 'administrator':
                status = "🆘Administrator!"
            elif chat_user_banned.status == 'creator':
                status = "🆘Creator!"
        else:
            if chat_user_banned.status == 'kicked':
                status = "🚨Banned"
            elif chat_user_banned.status == 'restricted':
                status = "⚠️Restricted"
            elif chat_user_banned.status == 'left':
                status = "✅️Not in group/not banned"
            elif chat_user_banned.status == 'member':
                status = "✅In group"
            elif chat_user_banned.status == 'administrator':
                status = "✅Administrator!"
            elif chat_user_banned.status == 'creator':
                status = "✅Creator!"

        text += "- {}: {}\n".format(group.title, status)

    return text


def __ban(bot: MQBot, ban_user: User, reason: str):
    """ Ban a  user and remove him from everywhere...

        1) Revoke right to interact with bot
        2) Remove user from assigned squad in bot
        3) For each group where bot is admin in with ban privileges:
            check if the user is in the group
            - if in the group, ban the user & notify group with "Long Ass Reason"
            - else, ban the user from the group
        4) for each group botato does not have admin privileges:
            - notify group with "Long Ass Reason"
    """

    # Create ban
    banned = Ban()
    banned.user_id = ban_user.id
    banned.from_date = datetime.now()
    banned.to_date = datetime.max
    banned.reason = reason or MSG_NO_REASON

    try:
        Session.add(banned)
        Session.commit()
    except SQLAlchemyError as ex:
        logging.error("[Ban] Can't save ban!")
        Session.rollback()
        return False

    # Delete user from squad
    member = Session.query(SquadMember).filter_by(user_id=ban_user.id).first()
    if member:
        logging.info("[Ban] Remove user_id='%s' from squad_id='%s'", ban_user.id, member.squad_id)
        Session.delete(member)

    # Remove Admin-Permissions
    admins = Session.query(Admin).filter_by(user_id=ban_user.id).all()
    for admin in admins:
        logging.info("[Ban] Removing admin-rights for user_id='%s'", ban_user.id)
        Session.delete(admin)

    # Save everything...
    Session.commit()

    disable_api_functions(ban_user)

    logging.info("[Ban] Saved ban and removed all access rights")

    all_active_groups = Session.query(Group).filter(
        Group.bot_in_group == True
    ).all()

    for group in all_active_groups:
        group_report = {}
        try:
            chat_user_banned = bot.get_chat_member(group.id, ban_user.id)
            chat_user_bot = bot.get_chat_member(group.id, bot.id)

            if chat_user_bot.status not in ['administrator', 'creator']:
                # Can't be kicked because we have no permissions
                bot.send_message(
                    chat_id=group.id,
                    text=MSG_USER_BANNED_UNAUTHORIZED.format(
                        '@' + ban_user.username if ban_user.username else ban_user.id,
                        banned.reason
                    ),
                )
            elif chat_user_banned.status in ['member', 'restricted']:
                # Currently a member. restrict + kick
                logging.info("[Ban] kick and restrict user_id='%s'", ban_user.id)
                bot.restrict_chat_member(group.id, ban_user.id)
                bot.kick_chat_member(group.id, ban_user.id)

                bot.send_message(
                    chat_id=group.id,
                    text=MSG_USER_BANNED.format(
                        '@' + ban_user.username if ban_user.username else ban_user.id,
                        banned.reason
                    ),
                )
            elif chat_user_banned.status == 'left':
                # Not a member. Just restrict
                bot.restrict_chat_member(group.id, ban_user.id)
            elif chat_user_banned.status in ['administrator', 'creator']:
                # Can't be kicked :-(
                bot.send_message(
                    chat_id=group.id,
                    text=MSG_USER_BANNED_UNAUTHORIZED.format(
                        '@' + ban_user.username if ban_user.username else ban_user.id,
                        banned.reason
                    ),
                )
        except Unauthorized as ex:
            bot.send_message(
                chat_id=group.id,
                text=MSG_USER_BANNED_UNAUTHORIZED.format(
                    '@' + ban_user.username if ban_user.username else ban_user.id,
                    banned.reason
                ),
            )
        except TelegramError as ex:
            logging.warning(
                "[Ban] Error banning user: %s",
                ex.message
            )

    # TODO: REENABLE!
    #send_async(bot, chat_id=ban_user.id, text=MSG_YOU_BANNED.format(banned.reason))

    return True


def __ban_traitor(bot: MQBot, user_id: int):
    ban_user = Session.query(User).filter(User.id == user_id).first()
    if ban_user:
        __ban(bot, ban_user, MSG_REASON_TRAITOR)

@command_handler(
    min_permission=AdminType.FULL
)
def unban(bot: MQBot, update: Update, user: User):
    username = update.message.text.split(' ', 1)[1]
    username = username.replace('@', '')
    unban_user = Session.query(User).filter_by(username=username).first()
    if not unban_user:
        try:
            # Try to find by ID
            unban_user = Session.query(User).filter(User.id == int(username)).first()
        except ValueError:
            pass

    if unban_user:
        banned = Session.query(Ban).filter_by(user_id=unban_user.id).first()
        if banned:
            logging.info("[Unban] user_id='%s' is banned. Lifting it.", unban_user.id)
            try:
                Session.delete(banned)
                Session.commit()
            except SQLAlchemyError:
                Session.rollback()

        logging.info("[Unban] Lifting chat restrictions for user_id='%s' regardless of ban status", unban_user.id)
        all_active_groups = Session.query(Group).filter(
            Group.bot_in_group == True
        ).all()
        for group in all_active_groups:
            group_report = {}
            try:
                chat_user_unbanned = bot.get_chat_member(group.id, unban_user.id)
                chat_user_bot = bot.get_chat_member(group.id, bot.id)

                if chat_user_unbanned.status in ['kicked', 'restricted']:
                    logging.info("[Ban] kick and restrict user_id='%s'", unban_user.id)
                    bot.restrict_chat_member(
                        chat_id=group.id,
                        user_id=unban_user.id,
                        #until_date=datetime.now()+timedelta(seconds=45),
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_other_messages=True,
                        can_add_web_page_previews=True,
                    )
            except Unauthorized as ex:
                bot.send_message(
                    chat_id=group.id,
                    text=MSG_USER_BANNED_UNAUTHORIZED.format(
                        '@' + unban_user.username if unban_user.username else unban_user.id,
                        banned.reason
                    ),
                )
            except TelegramError as ex:
                logging.warning(
                    "[Ban] Error banning user: %s",
                    ex.message
                )

        send_async(bot, chat_id=unban_user.id, text=MSG_YOU_UNBANNED)
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=__get_user_info(bot, unban_user),
            parse_mode=ParseMode.HTML
        )
    else:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_USER_UNKNOWN)


def __get_item_worth(item_name):
    r = redis.StrictRedis(host=REDIS_SERVER, port=REDIS_PORT, db=0)
    item_prices = r.lrange(item_name, 0, -1)
    item_prices = list(map(int, item_prices))

    if item_prices:
        return int(min(item_prices))
    return None


@command_handler()
def get_log(bot: MQBot, update: Update, user: User):
    if update.message.from_user.id not in LOG_ALLOWED_RECIPIENTS:
        logging.warning("User %s tried to request logs and is not allowed to!", update.message.from_user.id)
        return

    logging.info("User %s requrested logs", update.message.from_user.id)
    if update.message.chat.type == 'private':
        with open(LOGFILE, 'rb') as file:
            bot.send_document(
                chat_id=update.message.chat.id,
                document=file,
                timeout=120  # Logs can be big, so use a bigger timeout...
            )
