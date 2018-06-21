class MessageHandler:
    def __init__(self, condition, action):
        self.condition = condition
        self.action = action


class SimpleHandler(MessageHandler):
    def __init__(self, message, action):
        self.condition = lambda msg: msg == message.lower()
        self.action = action


class RegisteredOnlyHandler(MessageHandler):
    def __init__(self, message, action, is_registered):
        self.condition = lambda msg: msg == message.lower() and is_registered
        self.action = action


def handle_message(handlers, msg, bot, update):
    for handler in handlers:
        if handler.condition(msg):
            handler.action(bot, update)
            return True
    return False
