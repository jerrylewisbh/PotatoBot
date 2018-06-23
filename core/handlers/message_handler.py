import re


class MessageHandler:
    def __init__(self, condition, action):
        self.condition = condition
        self.action = action


class SimpleHandler(MessageHandler):
    def __init__(self, message, action):
        self.condition = lambda msg, update: msg.lower() == message.lower()
        self.action = action


class RegexHandler(MessageHandler):
    def __init__(self, regex, action):
        self.condition = lambda msg, update: re.search(regex, update.message.text)
        self.action = action


def handle_message(handlers, msg, bot, update):
    for handler in handlers:
        if handler.condition(msg=msg, update=update):
            handler.action(bot, update)
            return True
    return False
