import logging
from telegram import Bot
from telegram.ext.dispatcher import run_async


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@run_async
def send_async(bot: Bot, *args, **kwargs):
    bot.sendMessage(*args, **kwargs)