from _operator import or_

import codecs
import csv
import os
import sys
import urllib.request
from sqlalchemy import collate

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../botato')))

# noinspection PyPep8
from core.db import Session
from core.model import Item, ItemType

Session()

Session.query(Item).filter(Item.cw_id == '01').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '02').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '03').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '04').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '05').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '06').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '07').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '08').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '09').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '10').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '11').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '12').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '13').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '14').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '15').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '16').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '17').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '18').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '19').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '20').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '21').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '22').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '23').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '24').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '25').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '26').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '27').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '28').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '29').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '30').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '31').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '32').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '33').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '34').update({"item_type": ItemType.RES})
Session.query(Item).filter(Item.cw_id == '35').update({"item_type": ItemType.RES})

Session.query(Item).filter(Item.cw_id == '39').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '40').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '41').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '42').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '43').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '44').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '45').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '46').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '47').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '48').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '49').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '50').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '51').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '52').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '53').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '54').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '55').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '56').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '57').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '58').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '59').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '60').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '61').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '62').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '63').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '64').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '65').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '66').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '67').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '68').update({"item_type": ItemType.ALCH})
Session.query(Item).filter(Item.cw_id == '69').update({"item_type": ItemType.ALCH})

for item in Session.query(Item).filter(Item.cw_id.like('p%')).all():
    print(item.name)
    item.item_type = ItemType.MISC
    Session.add(item)

for item in Session.query(Item).filter(Item.cw_id.like('r%')).all():
    print(item.name)
    item.item_type = ItemType.OTHER
    Session.add(item)

for item in Session.query(Item).filter(Item.cw_id.like('w%')).all():
    print(item.name)
    item.item_type = ItemType.OTHER
    Session.add(item)

for item in Session.query(Item).filter(Item.cw_id.like('k%')).all():
    print(item.name)
    item.item_type = ItemType.OTHER
    Session.add(item)

for item in Session.query(Item).filter(Item.cw_id.like('a%')).all():
    print(item.name)
    item.item_type = ItemType.OTHER
    Session.add(item)


for item in Session.query(Item).filter(Item.cw_id.like('e%')).all():
    print(item.name)
    item.item_type = ItemType.OTHER
    Session.add(item)

Session.commit()
