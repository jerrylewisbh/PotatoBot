import codecs
import csv
import os
import sys
import urllib.request

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# noinspection PyPep8
from core.types import *

Session()

the_url = input("Url to Heroku Dataclip CSV: ")

with urllib.request.urlopen(the_url) as url:
    the_file = codecs.iterdecode(url, 'utf-8')
    for line in csv.DictReader(the_file):
        item = Session.query(Item).filter(
            Item.name == line['name'],
            Item.cw_id == None
        ).first()

        if item:
            print("Found missing cw_id='{}' for name='{}'".format(line['id'], line['name']))
            item.cw_id = line['id']
            Session.add(item)
            Session.commit()
