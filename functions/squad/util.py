from telegram import Bot, ParseMode, TelegramError

from core.texts import MSG_SQUAD_ALREADY_DELETED, MSG_SQUAD_LEFT
from core.types import User, Session, Admin
from core.utils import send_async
from functions.user.util import disable_api_functions


def __remove(bot: Bot, squad_user: User):
    """ Remove a given user from a squad if he is a member... """

    """ OLD CODE: 
        if squad_user.member.user_id == user.id:
        bot.edit_message_text(
            MSG_SQUAD_LEFT.format(member_user.character.name, squad.squad_name),
            message.chat.id,
            message.message_id, parse_mode=ParseMode.HTML
        )
    else:
        send_async(
            bot,
            chat_id=member.user_id,
            text=MSG_SQUAD_LEFT.format(member_user.character.name, squad.squad_name),
            parse_mode=ParseMode.HTML
        )

        members = Session.query(SquadMember).filter_by(squad_id=member.squad_id, approved=True).all()
        markups = generate_fire_up(members)
        for markup in markups:
            send_async(bot, chat_id=message.chat.id, text=message.text, reply_markup=markup)

    """

    if not squad_user.member:
        send_async(
            bot,
            chat_id=squad_user.id,
            text=MSG_SQUAD_ALREADY_DELETED
        )
        return

    # Inform ppl...
    if squad_user.member.approved:
        admins = Session.query(Admin).filter_by(admin_group=squad_user.member.squad.chat_id).all()
        print(squad_user.character.name, squad_user.member.squad.squad_name)
        for adm in admins:
            if adm.user_id != squad_user.id:
                send_async(
                    bot,
                    chat_id=adm.user_id,
                    text=MSG_SQUAD_LEFT.format(squad_user.character.name, squad_user.member.squad_name),
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
