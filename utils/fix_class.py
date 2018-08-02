import codecs
import csv
import os
import sys

from sqlalchemy import update

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../botato')))

# noinspection PyPep8
from core.db import Session
from core.model import Item, Character, Profession

Session()


c = Session.query(Character.user_id).distinct().all()

mapping = {
    'Master': 'Esquire / Master',
    'Esquire': 'Esquire / Master',
}

for user_id in c:
    user_id = user_id[0]
    user_profession = Session.query(Profession).filter(Profession.user_id == user_id).order_by(Profession.date.desc()).first()

    if not user_profession:
        continue

    if user_profession.name:
        print("Setting {} for {}".format(user_profession.name, user_id))
        Session.query(Character).filter(Character.user_id == user_id).update({"characterClass": mapping.get(user_profession.name, user_profession.name)})
        Session.commit()


