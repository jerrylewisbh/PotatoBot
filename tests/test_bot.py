#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import time
from telethon import events, TelegramClient
from telethon.tl.types import InputPeerChat, PeerChannel, InputPeerUser
from telethon.utils import get_input_peer

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core import commands
from core.handler import chats

api_id = 251026
api_hash = 'ed6af31198c04537c16dbc311060df20'

client = TelegramClient('session_name', api_id, api_hash)
client.updates.workers = 1
client.start()

for item in dir(commands):
    if not item.startswith("__"):
        #client.send_message('@KartoffelTheTestBot', getattr(commands, item))
        #time.sleep(1)
        pass


for item in dir(chats):
    if item.startswith("CC_"):
        print(item)
        chat = client.get_input_entity("https://t.me/joinchat/Coq1eULEPNMICdXA2kFwyA")
        client.send_message(chat, getattr(chats, item))
        time.sleep(1)
