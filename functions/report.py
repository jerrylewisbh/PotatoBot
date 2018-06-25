from telegram import Bot, Update

from config import FWD_BOT, FWD_CHANNEL
from core.decorators import command_handler
from core.texts import *
from core.types import *
from core.utils import update_group, send_async

Session()

@command_handler(
    allow_group=True,
    min_permission=AdminType.GROUP
)
def enable_report_fwd(bot: Bot, update: Update, user: User):
    if update.message.chat.type in ['group', 'supergroup']:
        group = update_group(update.message.chat)
        group.fwd_minireport = True
        Session.add(group)
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_MINI_REPORT_FWD_ENABLED)

@command_handler(
    allow_group=True,
    min_permission=AdminType.GROUP
)
def disable_report_fwd(bot: Bot, update: Update, user: User):
    if update.message.chat.type in ['group', 'supergroup']:
        group = update_group(update.message.chat)
        group.fwd_minireport = False
        Session.add(group)
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_MINI_REPORT_FWD_DISABLED)


def fwd_report(bot: Bot, update: Update):
    if not update.message.text or not update.message.text.startswith("⛳️Battle results"):
        # Nothing to do...
        return

    fwd_group = Session.query(Group).filter(
        Group.fwd_minireport == True,
        Group.bot_in_group == True,
        Group.id != FWD_CHANNEL
    ).all()

    for group in fwd_group:
        logging.debug("Forwarding report to '%s/%s'", group.id, group.title)

        print(update)
        bot.forward_message(
            chat_id=group.id,
            from_chat_id=FWD_CHANNEL,
            message_id=update.message.message_id
        )


