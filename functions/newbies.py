from telegram import Update

from config import ACADEM_CHAT_ID, CASTLE_CHAT_ID
from core.bot import MQBot
from core.decorators import command_handler
from core.template import fill_template
from core.texts import *
from core.types import Group, Session, User
from core.utils import send_async

Session()


@command_handler()
def newbie(bot: MQBot,update: Update, user: User):
    if ACADEM_CHAT_ID and CASTLE_CHAT_ID:
        if update.message.chat.id in [CASTLE_CHAT_ID]:
            for new_chat_member in update.message.new_chat_members:
                user = Session.query(User).filter(User.id == new_chat_member.id).first()
                if user is None:
                    group = Session.query(Group).filter(Group.id == ACADEM_CHAT_ID).first()
                    if group is not None:
                        send_async(bot, chat_id=group.id,
                                   text=fill_template(MSG_NEWBIE, new_chat_member))
