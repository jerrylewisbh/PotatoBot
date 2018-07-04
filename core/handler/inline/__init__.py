from uuid import uuid4

from telegram import (InlineQueryResultArticle, InputTextMessageContent)

from core.enums import CASTLE_LIST, TACTICTS_COMMAND_PREFIX, Castle
from core.types import (Session)
from functions.guild.stock import generate_gstock_requests

Session()


def inlinequery(bot, update):
    """Handle the inline query."""
    query = update.inline_query.query
    results = []

    if query in CASTLE_LIST or query.startswith(TACTICTS_COMMAND_PREFIX):
        results = [
            InlineQueryResultArticle(id=0,
                                     title=("DEFEND " if Castle.BLUE.value == query
                                                         or query.startswith(TACTICTS_COMMAND_PREFIX)
                                            else "ATTACK ") + query,
                                     input_message_content=InputTextMessageContent(query))]
    elif query.startswith("withdraw ") or query.startswith("deposit "):
        withdraw_requests = generate_gstock_requests(query)
        if withdraw_requests:
            for entry in withdraw_requests:
                results.append(
                    InlineQueryResultArticle(
                        id=uuid4(),
                        title=entry["label"],
                        input_message_content=InputTextMessageContent(entry["command"])
                    )
                )
    update.inline_query.answer(results)
