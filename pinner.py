from telethon import RPCError, TelegramClient
from telethon.tl import Session
from telethon.tl.types import UpdatesTg, UpdateNewChannelMessage, Message
from telethon.tl.functions.channels import UpdatePinnedMessageRequest
from telethon.utils import get_input_peer
from getpass import getpass
from time import sleep
from core.types import Admin, AdminType, session

API_ID = 119008
API_HASH = '5ac561f40e85417a5313ae9c230f9fc6'
client: TelegramClient = None


def auth(tg_client: TelegramClient):
    print('Connecting to Telegram servers...')
    tg_client.connect()

    # Then, ensure we're authorized and have access
    if not tg_client.is_user_authorized():
        phone = input('Enter your phone number: ')
        print('First run. Sending code request...')
        tg_client.send_code_request(phone)

        code_ok = False
        while not code_ok:
            code = input('Enter the code you just received: ')
            try:
                code_ok = tg_client.sign_in(phone, code)

            # Two-step verification may be enabled
            except RPCError as e:
                if e.password_required:
                    pw = getpass(
                        'Two step verification is enabled. Please enter your password: ')
                    code_ok = tg_client.sign_in(password=pw)
                else:
                    pass


def pin(message):
    try:
        client.invoke(UpdatePinnedMessageRequest(get_input_peer(message['channel']), message['id'], silent=False))
    except RPCError as e:
        print(e.message)


def receive(msg):
    if type(msg) is UpdatesTg:
        for upd in msg.updates:
            if type(upd) is UpdateNewChannelMessage:
                in_message = upd.message
                if type(in_message) is Message:
                    if not in_message.out:
                        channel = None
                        for chat in msg.chats:
                            if chat.id == in_message.to_id.channel_id:
                                channel = chat
                        admin = session.query(Admin).filter(Admin.user_id == in_message.from_id,
                                                            Admin.admin_group.in_([0,
                                                                                   '-100' + str(channel.id)])).first()
                        if in_message.from_id == 386494081 and in_message.reply_markup:
                            message = {}
                            message['channel'] = channel
                            message['id'] = in_message.id
                            pin(message)
                        elif admin is not None and admin.admin_type <= AdminType.GROUP.value and \
                                in_message.reply_to_msg_id and \
                                in_message.message.upper() in ['запинь'.upper(), 'пин'.upper()]:
                            message = {}
                            message['channel'] = channel
                            message['id'] = in_message.reply_to_msg_id
                            pin(message)


def main():
    global client
    session = Session.try_load_or_create_new('pinner')
    session.server_address = '149.154.167.50'
    session.port = 443
    client = TelegramClient(session, API_ID, API_HASH)
    auth(client)
    client.add_update_handler(receive)
    while 1:
        sleep(1)


if __name__ == '__main__':
    main()
