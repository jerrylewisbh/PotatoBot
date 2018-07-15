import os
import sys

from sqlalchemy import text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../botato/')))

# noinspection PyPep8
from core.db import Session
from core.model import Group

Session()

result = Session.execute(text('SELECT chat_id, reminders_enabled, thorns_enabled, silence_enabled FROM squads'))
for squad in result:
    group = Session.query(Group).filter(Group.id == squad[0]).first()
    group.reminders_enabled = squad[1]
    group.thorns_enabled = squad[2]
    group.silence_enabled = squad[3]
    Session.add(group)
    Session.commit()
