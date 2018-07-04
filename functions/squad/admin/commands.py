from telegram import Update, ParseMode, TelegramError

from core.bot import MQBot
from core.decorators import command_handler
from core.texts import MSG_SQUAD_THORNS_ENABLED, MSG_SQUAD_REMINDERS_ENABLED, MSG_SQUAD_SILENCE_ENABLED, \
    MSG_SQUAD_THORNS_DISABLED, MSG_SQUAD_SILENCE_DISABLED, MSG_SQUAD_REMINDERS_DISABLED, MSG_SQUAD_RECRUITING_ENABLED, \
    MSG_SQUAD_RECRUITING_DISABLED, MSG_SQUAD_NEW, MSG_SQUAD_LINK_SAVED, MSG_SQUAD_RENAMED, MSG_SQUAD_DELETE, \
    MSG_SQUAD_NO_PROFILE, MSG_SQUAD_ADD_IN_SQUAD, MSG_SQUAD_ADD_FORCED, MSG_SQUAD_ADD
from core.types import AdminType, User, Session, Group, Squad, SquadMember
from core.utils import send_async
from functions.squad import generate_squad_invite_answer


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def enable_thorns(bot: MQBot, update: Update, _user: User):
    group = Session.query(Group).filter_by(id=update.message.chat.id).first()
    if group and len(group.squad) == 1:
        group.squad[0].thorns_enabled = True
        Session.add(group.squad[0])
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_THORNS_ENABLED)


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def enable_reminders(bot: MQBot, update: Update, user: User):
    group = Session.query(Group).filter_by(id=update.message.chat.id).first()
    if group and len(group.squad) == 1:
        group.squad[0].reminders_enabled = True
        Session.add(group.squad[0])
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_REMINDERS_ENABLED)


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def enable_silence(bot: MQBot, update: Update, user: User):
    group = Session.query(Group).filter_by(id=update.message.chat.id).first()
    if group and len(group.squad) == 1:
        group.squad[0].silence_enabled = True
        Session.add(group.squad[0])
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_SILENCE_ENABLED)


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def disable_thorns(bot: MQBot, update: Update, user: User):
    group = Session.query(Group).filter_by(id=update.message.chat.id).first()
    if group and len(group.squad) == 1:
        group.squad[0].thorns_enabled = False
        Session.add(group.squad[0])
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_THORNS_DISABLED)


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def disable_silence(bot: MQBot, update: Update, user: User):
    group = Session.query(Group).filter_by(id=update.message.chat.id).first()
    if group and len(group.squad) == 1:
        group.squad[0].silence_enabled = False
        Session.add(group.squad[0])
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_SILENCE_DISABLED)


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def disable_reminders(bot: MQBot, update: Update, user: User):
    group = Session.query(Group).filter_by(id=update.message.chat.id).first()
    if group and len(group.squad) == 1:
        group.squad[0].reminders_enabled = False
        Session.add(group.squad[0])
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_REMINDERS_DISABLED)


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def open_hiring(bot: MQBot, update: Update, user: User):
    squad = Session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
    if squad is not None:
        squad.hiring = True
        Session.add(squad)
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_RECRUITING_ENABLED)


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def close_hiring(bot: MQBot, update: Update, user: User):
    squad = Session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
    if squad is not None:
        squad.hiring = False
        Session.add(squad)
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_RECRUITING_DISABLED)


@command_handler(
    min_permission=AdminType.FULL,
    allow_private=False,
    allow_group=True
)
def add_squad(bot: MQBot, update: Update, user: User):
    squad = Session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
    if squad is None:
        squad = Squad()
        squad.chat_id = update.message.chat.id
        squad.thorns_enabled = False
        msg = update.message.text.split(' ', 1)
        if len(msg) == 2:
            squad.squad_name = msg[1]
        else:
            group = Session.query(Group).filter_by(id=update.message.chat.id).first()
            squad.squad_name = group.title
        Session.add(squad)
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_NEW.format(squad.squad_name),
                   parse_mode=ParseMode.HTML)


@command_handler(
    min_permission=AdminType.FULL,
    allow_private=False,
    allow_group=True
)
def set_invite_link(bot: MQBot, update: Update, user: User):
    squad = Session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
    new_invite_link = ''
    if squad:
        msg = update.message.text.split(' ', 1)
        if len(msg) == 2:
            new_invite_link = msg[1]
        else:
            try:
                new_invite_link = bot.export_chat_invite_link(update.effective_chat.id)
            except TelegramError:  # missing add_user admin permission
                return

    if new_invite_link:
        squad.invite_link = new_invite_link
        Session.add(squad)
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_LINK_SAVED)


@command_handler(
    min_permission=AdminType.FULL,
    allow_private=False,
    allow_group=True
)
def set_squad_name(bot: MQBot, update: Update, user: User):
    squad = Session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
    if squad:
        msg = update.message.text.split(' ', 1)
        if len(msg) == 2:
            squad.squad_name = msg[1]
            Session.add(squad)
            Session.commit()
            send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_RENAMED.format(squad.squad_name),
                       parse_mode=ParseMode.HTML)


@command_handler(
    min_permission=AdminType.FULL,
    allow_private=False,
    allow_group=True
)
def del_squad(bot: MQBot, update: Update, user: User):
    squad = Session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
    if squad:
        for member in squad.members:
            Session.delete(member)
        for order_group_item in squad.chat.group_items:
            Session.delete(order_group_item)
        Session.delete(squad)
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_DELETE)


@command_handler(
    min_permission=AdminType.FULL,
    allow_private=False,
    allow_group=True
)
def force_add_to_squad(bot: MQBot, update: Update, user: User):
    squad = Session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
    if squad is not None:
        username = update.message.text.split(' ', 1)
        if len(username) == 2:
            username = username[1].replace('@', '')
            user = Session.query(User).filter_by(username=username).first()
            if user is not None:
                if user.character is None:
                    send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_NO_PROFILE)
                elif user.member is not None:
                    send_async(bot, chat_id=update.message.chat.id,
                               text=MSG_SQUAD_ADD_IN_SQUAD.format('@' + username))
                else:
                    member = Session.query(SquadMember).filter_by(user_id=user.id).first()
                    if member is None:
                        member = SquadMember()
                        member.user_id = user.id
                        member.squad_id = update.message.chat.id
                        member.approved = True
                        Session.add(member)
                        Session.commit()
                        send_async(
                            bot,
                            chat_id=update.message.chat.id,
                            text=MSG_SQUAD_ADD_FORCED.format(
                                '@' + user.username))


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def add_to_squad(bot: MQBot, update: Update, user: User):
    squad = Session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
    if squad is not None:
        username = update.message.text.split(' ', 1)
        if len(username) == 2:
            username = username[1].replace('@', '')
            user = Session.query(User).filter_by(username=username).first()
            if user is not None:
                if user.character is None:
                    send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_NO_PROFILE)
                elif user.member is not None:
                    send_async(bot, chat_id=update.message.chat.id,
                               text=MSG_SQUAD_ADD_IN_SQUAD.format('@' + username))
                else:
                    markup = generate_squad_invite_answer(user.id)
                    send_async(bot, chat_id=update.message.chat.id,
                               text=MSG_SQUAD_ADD.format('@' + username),
                               reply_markup=markup)
