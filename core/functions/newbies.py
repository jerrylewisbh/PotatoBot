from telegram import Update, Bot
from core.types import User, Group, user_allowed
from core.template import fill_template
from core.utils import send_async
from core.texts import *
from config import ACADEM_CHAT_ID, CASTLE_CHAT_ID

@user_allowed
def newbie(bot: Bot, update: Update, session):
    if ACADEM_CHAT_ID and CASTLE_CHAT_ID:
        if update.message.chat.id in [CASTLE_CHAT_ID]:
            if update.message.new_chat_member is not None:
                user = session.query(User).filter(User.id == update.message.new_chat_member.id).first()
                if user is None:
                    group = session.query(Group).filter(Group.id == ACADEM_CHAT_ID).first()
                    if group is not None:
                        send_async(bot, chat_id=group.id,
                                   text=fill_template(MSG_NEWBIE, update.message.new_chat_member))
