import codecs
import csv
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../botato')))

# noinspection PyPep8
from core.db import Session
from core.model import Item, Character, Profession

Session()


c = Session.query(Character).all()

for char in c:
    user_profession = Session.query(Profession).filter(
        Profession.user_id == char.user_id
    ).order_by(Profession.date.desc()).first()

    if not user_profession:
        continue

    if char.characterClass != user_profession.name:
        print("Setting {} for {}".format(user_profession.name, char.name))
        char.characterClass = user_profession.name
        Session.add(char)
        Session.commit()


