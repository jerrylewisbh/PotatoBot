import logging

from sqlalchemy.exc import SQLAlchemyError
from telegram import ParseMode, TelegramError

from core.bot import MQBot
from core.utils import send_async
from core.texts import MSG_SQUAD_ALREADY_DELETED, MSG_SQUAD_LEFT
from core.db import Session
from core.model import User, Admin, SquadMember
from functions.admin import __kickban_from_chat
from functions.user.util import disable_api_functions


def __remove(bot: MQBot, user: User, squad_user: User):
    """ Remove a given user from a squad if he is a member... """

    if not squad_user.member:
        send_async(
            bot,
            chat_id=squad_user.id,
            text=MSG_SQUAD_ALREADY_DELETED
        )
        return

    # Inform ppl...
    if squad_user.member.approved:
        admins = Session.query(Admin).filter_by(group_id=squad_user.member.squad.chat_id).all()
        for adm in admins:
            # Notify Admins, except for the one who triggered it because he already gets a notification
            if adm.user_id != squad_user.id and adm.user_id != user.id:
                send_async(
                    bot,
                    chat_id=adm.user_id,
                    text=MSG_SQUAD_LEFT.format(squad_user.character.name, squad_user.member.squad.squad_name),
                    parse_mode=ParseMode.HTML
                )

        send_async(
            bot,
            chat_id=squad_user.member.squad.chat_id,
            text=MSG_SQUAD_LEFT.format(squad_user.character.name, squad_user.member.squad.squad_name),
            parse_mode=ParseMode.HTML
        )

    # Try to remove user...
    __kickban_from_chat(bot, squad_user, squad_user.member.squad.chat)

    # Disable API related stuff and remove him from squad
    old_squad = squad_user.member.squad.squad_name
    disable_api_functions(squad_user)
    Session.delete(squad_user.member)
    Session.commit()

    return old_squad


def __add_member(bot: MQBot, user_id: int, squad_id: int):
    """ Add a person to a squad if he is not already in a squad... Also: Unban that user from this chat
    if he is banned"""
    logging.info("Adding user_id='%s' to squad_id='%s'", user_id, squad_id)
    member = Session.query(SquadMember).filter_by(user_id=user_id).first()
    if not member:
        member = SquadMember()
        member.user_id = user_id
        member.squad_id = squad_id
        member.approved = True

        try:
            logging.info("Issuing 'unban' for user if needed: %s", user_id)
            bot.unban_chat_member(
                chat_id=squad_id,
                user_id=user_id
            )
        except Exception as ex:
            logging.warning("Error unbanning user: %s", ex.message)

        try:
            Session.add(member)
            Session.commit()
        except SQLAlchemyError:
            logging.error("Error adding SquadMember user_id='%s'", user_id)
            Session.rollback()

        return True

    return False
