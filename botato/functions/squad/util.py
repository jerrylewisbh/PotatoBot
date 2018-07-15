from telegram import ParseMode, TelegramError

from core.bot import MQBot
from core.texts import MSG_SQUAD_ALREADY_DELETED, MSG_SQUAD_LEFT
from core.db import Session
from core.model import User, Admin
from core.utils import send_async
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
    try:
        bot.restrict_chat_member(squad_user.member.squad.chat_id, squad_user.id)
        bot.kick_chat_member(squad_user.member.squad.chat_id, squad_user.id)
    except TelegramError as err:
        bot.logger.error(err.message)

    # Disable API related stuff and remove him from squad
    old_squad = squad_user.member.squad.squad_name
    disable_api_functions(squad_user)
    Session.delete(squad_user.member)
    Session.commit()

    return old_squad
