import logging
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.db import Session
from core.model import User, Character, Squad, SquadMember
from functions.battle import create_user_report

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Logging for console
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

api_users = Session.query(User).join(SquadMember).join(Squad).join(Character).filter(
    User.api_token is not None,
    SquadMember.approved.is_(True),
).all()

for user in api_users:
    logging.info("report_after_battle for user_id='%s'", user.id)

    logging.info(create_user_report(user))

    logging.info("END report_after_battle for user_id='%s'", user.id)
