import logging
from datetime import datetime
from enum import IntFlag, auto
from html import escape

from sqlalchemy.exc import SQLAlchemyError
from telegram import Update, ParseMode
from telegram.error import Unauthorized, BadRequest, TelegramError

from config import LOG_ALLOWED_RECIPIENTS, LOGFILE, GOVERNMENT_CHAT
from core.bot import MQBot
from core.db import Session
from core.decorators import command_handler
from core.enums import AdminType
from core.model import User, Admin, Group, Ban, SquadMember
from core.texts import *
from core.utils import send_async, update_group, disable_group
from functions.reply_markup import generate_admin_markup
from functions.user.util import disable_api_functions

class KickBanResult(IntFlag):
    KICKED = auto() # Kicked
    GROUP_MEMBER = auto() # Is/Was group member
    PERMISSION_FAILURE = auto() # Can't kick...


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
def kickban(bot: MQBot, update: Update, user: User):
    group = Session.query(Group).filter(Group.id == update.effective_chat.id).first()
    ban_user = Session.query(User).filter(User.id == update.message.reply_to_message.from_user.id).first()

    if group and ban_user:
        result = __kickban_from_chat(
            bot,
            ban_user,
            group
        )
        if KickBanResult.KICKED in result and KickBanResult.GROUP_MEMBER in result:
            bot.send_message(
                chat_id=group.id,
                text=MSG_USER_BANNED_NO_REASON.format(
                    '@' + ban_user.username if ban_user.username else ban_user.id,
                ),
            )
        else:
            logging.warning(
                "[Kickban] Couldn't kick and ban user_id='%s' from group_id='%s'",
                ban_user.id,
                group.id
            )
    else:
        logging.warning(
            "[Kickban] Couldn't kick and ban based on given data: %s",
            update
        )


def __kickban_from_chat(bot: MQBot, ban_user: User, group: Group):
    """ This will kick and ban ban_user from given group

    :returns boolean True if user is kicked
    """

    try:
        chat_user_banned = bot.get_chat_member(group.id, ban_user.id)
        chat_user_bot = bot.get_chat_member(group.id, bot.id)

        if chat_user_bot.status not in ['administrator', 'creator']:
            # Can't be kicked because we have no permissions
            logging.warning(
                "[Ban] can't kick and restrict user_id='%s' from chat_id='%s' because bot has no permission",
                ban_user.id,
                group.id
            )
            return KickBanResult.PERMISSION_FAILURE
        elif chat_user_banned.status in ['member', 'restricted']:
            # Currently a member. restrict + kick
            logging.info(
                "[Ban] kick and ban user_id='%s' from chat_id='%s'",
                ban_user.id,
                group.id
            )
            bot.kick_chat_member(group.id, ban_user.id)
            return KickBanResult.KICKED | KickBanResult.GROUP_MEMBER
        elif chat_user_banned.status == 'left':
            # Not a member.
            logging.info(
                "[Ban] restrict user_id='%s' from chat_id='%s'",
                ban_user.id,
                group.id
            )
            bot.kick_chat_member(group.id, ban_user.id)
            return KickBanResult.KICKED
        elif chat_user_banned.status in ['administrator', 'creator']:
            # Can't be kicked...
            logging.warning(
                "[Ban] Can't kick and ban user_id='%s' from chat_id='%s' since he is an administrator!",
                ban_user.id,
                group.id
            )
            return KickBanResult.PERMISSION_FAILURE
    except Unauthorized as ex:
        logging.warning(
            "[Ban] Can't kick and ban user_id='%s' from chat_id='%s' since he is an administrator!",
            ban_user.id,
            group.id
        )
        return KickBanResult.PERMISSION_FAILURE
    except BadRequest as ex:
        if ex.message == "Chat not found":
            logging.warning(
                "[Ban] Chat for group_id='%s' not found: %s",
                group.id,
                ex.message
            )
            disable_group(group)
        else:
            logging.warning(
                "[Ban] Can't unban in group_id='%s'. Message: %s",
                group.id,
                ex.message
            )
    except TelegramError as ex:
        logging.warning(
            "[Ban] Error banning user: %s",
            ex.message
        )

    return KickBanResult.PERMISSION_FAILURE


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
                was_banned = __ban_globally(bot, ban_user, reason)
                if was_banned:
                    send_async(
                        bot,
                        chat_id=update.message.chat.id,
                        text=MSG_BAN_COMPLETE
                    )
                    send_async(
                        bot,
                        chat_id=update.message.chat_id,
                        text=__get_user_info(bot, ban_user),
                        parse_mode=ParseMode.HTML,
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
def ban_info_all(bot: MQBot, update: Update, user: User):
    """ Check all bans """

    text = "<b>Banned users:</b>\n"

    all_banned = Session.query(Ban).all()
    for ban in all_banned:
        text += "{}: {}\n".format(
            ban.user.username if ban.user.username else ban.user.id,
            ban.reason
        )
        send_async(
            bot,
            chat_id=update.message.chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
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
        user_info = None
        try:
            user_info = bot.get_chat_member(group.id, ban_user.id)
        except BadRequest as ex:
            if ex.message == "Chat not found":
                logging.warning(
                    "[User-Info] Chat for group_id='%s' not found: %s",
                    group.id,
                    ex.message
                )
                disable_group(group)
            else:
                logging.warning(
                    "[User-Info] Can't get info for user in group_id='%s'. Message: %s",
                    group.id,
                    ex.message
                )
        except TelegramError as ex:
            logging.warning(
                "[User-Info] TelegramError: %s", ex.message
            )

        status = "❓ Unknown"
        if not user_info:
            status = "❓ Unknown. Bot is probably no member of channel"
        elif ban_user.is_banned:
            if user_info.status == 'kicked':
                status = "✅Banned"
            elif user_info.status == 'left':
                status = "⚠️Not in group but not banned! (Missing Bot-Permissions?)"
            elif user_info.status == 'restricted':
                status = "⚠️Restricted but not banned!"
            elif user_info.status == 'member':
                status = "🚨In group (unbanned!)"
            elif user_info.status == 'administrator':
                status = "🆘Administrator!"
            elif user_info.status == 'creator':
                status = "🆘Creator!"
        else:
            if user_info.status == 'kicked':
                status = "🚨Banned"
            elif user_info.status == 'restricted':
                status = "⚠️Restricted"
            elif user_info.status == 'left':
                status = "✅️Not in group/not banned"
            elif user_info.status == 'member':
                status = "✅In group"
            elif user_info.status == 'administrator':
                status = "✅Administrator!"
            elif user_info.status == 'creator':
                status = "✅Creator!"

        text += "- {}: {}\n".format(group.title, status)

    return text


def __ban_globally(bot: MQBot, ban_user: User, reason: str):
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

    failed_bans = []
    for group in all_active_groups:
        result = __kickban_from_chat(bot, ban_user, group)
        if KickBanResult.KICKED in result and KickBanResult.GROUP_MEMBER in result:
            bot.send_message(
                chat_id=group.id,
                text=MSG_USER_BANNED.format(
                    '@' + ban_user.username if ban_user.username else ban_user.id,
                    banned.reason
                ),
            )
        elif KickBanResult.KICKED in result:
            logging.info("User was kicked/banned but was no group member")
        elif KickBanResult.PERMISSION_FAILURE in result:
            logging.warning("Can't ban user because of permissions fail: %s", ban_user.id)
            failed_bans.append(group.title)

    ban_fail_txt = "Failed groups:"
    if failed_bans:
        for group_name in failed_bans:
            ban_fail_txt += group_name
            ban_fail_txt += "\n"

        bot.send_message(
            chat_id=GOVERNMENT_CHAT,
            text=MSG_USER_BANNED_UNAUTHORIZED.format(
                '@' + ban_user.username if ban_user.username else ban_user.id,
                banned.reason,
                ban_fail_txt
            )
        )


    # TODO: REENABLE!
    #send_async(bot, chat_id=ban_user.id, text=MSG_YOU_BANNED.format(banned.reason))

    return True


def __ban_traitor(bot: MQBot, user_id: int):
    ban_user = Session.query(User).filter(User.id == user_id).first()
    if ban_user:
        __ban_globally(bot, ban_user, MSG_REASON_TRAITOR)


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
                    logging.info("[Unban] kick and restrict user_id='%s'", unban_user.id)
                    bot.unban_chat_member(
                        chat_id=group.id,
                        user_id=unban_user.id
                    )
            except Unauthorized as ex:
                logging.warning("Unauthorized: Unban for %s failed", unban_user.id)
            except BadRequest as ex:
                if ex.message == "Chat not found":
                    logging.warning(
                        "[Unban] Chat for group_id='%s' not found: %s",
                        group.id,
                        ex.message
                    )
                    disable_group(group)
                else:
                    logging.warning(
                        "[Unban] Can't unban in group_id='%s'. Message: %s",
                        group.id,
                        ex.message
                    )
            except TelegramError as ex:
                logging.error(
                    "[Unban] Error unbanning user: %s",
                    ex.message
                )



        send_async(bot, chat_id=unban_user.id, text=MSG_YOU_UNBANNED)
        send_async(
            bot,
            chat_id=update  .message.chat.id,
            text=__get_user_info(bot, unban_user),
            parse_mode=ParseMode.HTML
        )
    else:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_USER_UNKNOWN)


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
