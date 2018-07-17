""" Tool to make queues empty after bot was down for a longer time.... """

import os
import sys
import time

from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../botato')))

from config import CASTLE

from sqlalchemy import func, tuple_, collate

from core.db import Session
from core.model import Character, User

# noinspection PyPep8

SRCH = 176862585

character_class='%'
condition = Character.attack.desc()

newest_profiles = Session.query(
    Character.user_id,
    func.max(Character.date)
).group_by(Character.user_id).all()

for newest in newest_profiles:
    if newest[0] == SRCH:
        print("RENGAROOOOO!")

characters = Session.query(Character).filter(
    tuple_(Character.user_id, Character.date).in_([(a[0], a[1]) for a in newest_profiles]),
    Character.date > datetime.now() - timedelta(days=7),
    Character.castle == collate(CASTLE, 'utf8mb4_unicode_520_ci'),
    Character.characterClass.ilike(character_class)
).join(User).order_by(condition).all()

for char in characters:
    if char.user_id == SRCH:
        print("dis too!?")
