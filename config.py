"""
Settings class, which contains all information about to comminucate with game's servers,
such as the bq159_key, sakura session, game version, APIs hosts etc...
"""
import cryption
import requests
import sys
# API
version = 'gb'
now_version = '13.0.0'
bot_version = '1.22'
# This is the session_id, initialized in auth.py
sakura_session = None
init_session_key = None
bq159_key = None
session_key = None

# User info
username = ''
platform = 'ios'
uuid = None
udid = None
adid = None
deck = 1
ship = []
team = []
box_limit = 0
user_characters_nb = 0
select_friend = True
toggle_summon = False
friend_id = 12760
discord = True
premium = True
toggle_meat = True

# Functions
session = requests.Session()


def init_session_1():
    headers = {
        'Host': get_host(),
        'Content-type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': get_user_agent(),
        'Authorization': 'Basic c2FrdXJhOjBubHkwbmU=',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'close'
    }
    session.headers.update(headers)


def init_session_2():
    headers = {
        'Host': get_host(),
        'Content-type': 'application/json',
        'X-SESSION': sakura_session,
        'Accept': 'application/json',
        'User-Agent': get_user_agent(),
        'Authorization': 'Basic c2FrdXJhOjBubHkwbmU=',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'close'
    }
    session.headers.update(headers)


def get_session_key():
    global session_key

    if session_key:
        cryption.ReleaseBuffer(session_key)
    if init_session_key:
        cryption.ReleaseBuffer(init_session_key)
    return session_key


def get_user_agent():
    if version == 'jp':
        if platform == 'android':
            return f'sakura/{now_version} (Android; 7.1.2; SM-G935F)'
        else:
            return f'sakura/{now_version} (iPhone; 15.3.1; iPhone14,5)'

    elif version == 'gb':
        if platform == 'android':
            return f'sakura/{now_version} (Android; 7.1.2; SM-G935F)'
        else:
            return f'sakura/{now_version} (iPhone; 15.3.1; iPhone14,5)'

    else:
        print("error when retreiving version")
        sys.exit(0)


def get_version():
    if version == 'jp':
        return 'https://app.onepiece-tc.jp'
    elif version == 'gb':
        return 'https://app.gb.onepiece-tc.jp'
    else:
        print("error when retreiving version")
        sys.exit(0)


def get_host():
    if version == 'jp':
        return 'app.onepiece-tc.jp'
    elif version == 'gb':
        return 'app.gb.onepiece-tc.jp'
    else:
        print("error when retreiving host")
        sys.exit(0)
