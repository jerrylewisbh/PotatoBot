import logging
from html import escape

from telegram import Bot, ParseMode

from core.utils import send_async

# This code is based on python-telegram-handler from
# from https://github.com/sashgorokhov/python-telegram-handler
# Licence: https://github.com/sashgorokhov/python-telegram-handler/blob/master/LICENSE

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

__all__ = ['TelegramHandler']

class TelegramHandler(logging.Handler):
    last_response = None

    def __init__(self, bot: Bot, chat_id=None, level=logging.NOTSET, timeout=2, disable_notification=False,
                 disable_web_page_preview=False):
        self.bot = bot
        self.disable_web_page_preview = disable_web_page_preview
        self.disable_notification = disable_notification
        self.timeout = timeout
        self.chat_id = chat_id or self.get_chat_id()
        if not self.chat_id:
            level = logging.NOTSET
            logger.error('Did not get chat id. Setting handler logging level to NOTSET.')
        logger.info('Chat id: %s', self.chat_id)
        super(TelegramHandler, self).__init__(level=level)
        self.setFormatter(HtmlFormatter())

    @classmethod
    def format_url(cls, token, method):
        return 'https://api.telegram.org/bot%s/%s' % (token, method)

    def send_message(self, text, **kwargs):
        send_async(
            self.bot,
            chat_id=self.chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
         )

    def emit(self, record):
        text = self.format(record)
        data = {
            'chat_id': self.chat_id,
            'disable_web_page_preview': self.disable_web_page_preview,
            'disable_notification': self.disable_notification,
        }

        if getattr(self.formatter, 'parse_mode', None):
            data['parse_mode'] = self.formatter.parse_mode

        response = self.send_message(text, **data)
        if not response:
            return

        if not response.get('ok', False):
            logger.warning('Telegram responded with ok=false status! {}'.format(response))


class TelegramFormatter(logging.Formatter):
    """Base formatter class suitable for use with `TelegramHandler`"""

    fmt = "%(asctime)s %(levelname)s\n[%(name)s:%(funcName)s]\n%(message)s"
    parse_mode = None

    def __init__(self, fmt=None, *args, **kwargs):
        super(TelegramFormatter, self).__init__(fmt or self.fmt, *args, **kwargs)

class EMOJI:
    WHITE_CIRCLE = '⚪'
    BLUE_CIRCLE = '🔵'
    HEAVY_CIRCLE = '⭕'
    RED_CIRCLE = '🔴'


class HtmlFormatter(TelegramFormatter):
    """HTML formatter for telegram."""
    fmt = '<pre>%(levelname)s %(asctime)s\nFrom %(name)s:%(funcName)s\n%(message)s</pre>'
    parse_mode = 'HTML'

    def __init__(self, *args, **kwargs):
        self.use_emoji = kwargs.pop('use_emoji', False)
        super(HtmlFormatter, self).__init__(*args, **kwargs)

    def format(self, record):
        """
        :param logging.LogRecord record:
        """
        super(HtmlFormatter, self).format(record)

        if record.funcName:
            record.funcName = escape(str(record.funcName))
        if record.name:
            record.name = escape(str(record.name))
        if record.msg:
            record.msg = escape(record.getMessage())
        if self.use_emoji:
            if record.levelno == logging.DEBUG:
                record.levelname = EMOJI.WHITE_CIRCLE
            elif record.levelno == logging.INFO:
                record.levelname = EMOJI.BLUE_CIRCLE
            elif record.levelno == logging.WARNING:
                record.levelname = EMOJI.HEAVY_CIRCLE
            else:
                record.levelname = EMOJI.RED_CIRCLE

        return self.fmt % record.__dict__

    def formatException(self, *args, **kwargs):
        string = super(HtmlFormatter, self).formatException(*args, **kwargs)
        return '<pre>%s</pre>' % escape(string)
