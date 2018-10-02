from telegram import Update, ParseMode

from core.bot import MQBot
from core.decorators import command_handler
from core.model import User
from core.texts import *
from core.utils import send_async


@command_handler()
def guild_info(bot: MQBot, update: Update, _user: User):
    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=MSG_INFO_GUILD,
        parse_mode=ParseMode.HTML,
    )
