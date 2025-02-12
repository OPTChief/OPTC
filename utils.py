import urllib.parse
import re
import uuid
import random
import string
import base64
from Crypto.Cipher import AES
import secrets
import config
"""
Utils class, contains usefull functions we dont want in other classes.
"""

def generate_idfa():
    """
    Return Identifier for Advertiser (IDFA) for iOS account creation. (UDID)
    """
    return str(uuid.uuid4()).upper()

def generate_gaid():
    """
    Return Google Advertising ID (GAID) for Android account creation. (ADID)
    """
    return str(uuid.uuid1())

def generate_uuid():
    """
    Generates UniqueID Bandais servers
    """
    return str(uuid.uuid4()) 

def get_url_from_string(url):
    """
    Return URL for facebook translfer process, to use in custom web browser
    """
    string = url
    parsed_string = urllib.parse.urlsplit(string)
    redirect_uri = parsed_string.geturl()
    return redirect_uri

def get_code_and_state_from_url(url):
    """
    Return code & state for facebook transfer process
    """
    parsed_url = urllib.parse.urlsplit(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)

    code = query_params.get("code")[0]
    state = query_params.get("state")[0]
    return code, state

def get_token_from_html(html_body):
    """
    Return token for facebook transfer process
    """
    string = html_body
    match = re.search(r'token=(\w+)', string)

    if match:
        token = match.group(1)
        return token
    else:
        print("Token not found")
        return None


def get_card_url(id):
    padded_id = str(id).zfill(4)
    return f"https://cdn.gb.onepiece-tc.jp/en/images/characters/character_{padded_id}_t.png"

def format_deck_json(ship_id, char_ids):
    #Example : char_ids = [1, 2, 3, 4, 5], ship_id = 105369439299309667.
    deck_str = '"deck_type": 1, "decks": ['
    char_index = 0
    char_str = '{'
    for j in range(1, 6):
        if char_index >= len(char_ids):
            char_str += f'"{j}": {{ "user_character_id": null, "versus_child_character_id": null, "default_multiple_child_character_index": null, "support_user_character_id": null }},'
        else:
            char_str += f'"{j}": {{ "user_character_id": {char_ids[char_index]}, "versus_child_character_id": null, "default_multiple_child_character_index": null, "support_user_character_id": null }},'
            char_index += 1
    char_str = char_str[:-1] + '}'
    for i in range(8):
        deck_str += f'{{ "user_deck_characters": {char_str}, "user_ship": {ship_id}'
        if i == 0:
            deck_str += ', "active": true'
        deck_str += '},'
    deck_str = deck_str[:-1] + ']'
    return '{' + deck_str + '}'



def format_deck_json_v1(ship_id, char_id):
    deck_str = '"deck_type": 1, "decks": ['
    for i in range(8):
        char_str = '{'
        char_str += f'"1": {{ "user_character_id": {char_id}, "versus_child_character_id": null, "default_multiple_child_character_index": null, "support_user_character_id": null }},'
        for j in range(2, 6):
            char_str += f'"{j}": {{ "user_character_id": null, "versus_child_character_id": null, "default_multiple_child_character_index": null, "support_user_character_id": null }},'
        char_str = char_str[:-1] + '}'
        deck_str += f'{{ "user_deck_characters": {char_str}, "user_ship": {ship_id}'
        if i == 0:
            deck_str += ', "active": true'
        deck_str += '},'
    deck_str = deck_str[:-1] + ']'
    return '{' + deck_str + '}'

def deck_pvp(id):
    for a in id:
        deck_str = '{"user_pirates_decks": [{"position": 1,"deck_type": 1,"active": true,"user_pirates_deck_characters": [{"position": 1,"user_character_id":'f'{a},''"character_type": 1,"versus_child_character_id": null},{"position": 2,"user_character_id": null,"character_type": 1,"versus_child_character_id": null},{"position": 3,"user_character_id": null,"character_type": 1,"versus_child_character_id": null},{"position": 4,"user_character_id": null,"character_type": 1,"versus_child_character_id": null},{"position": 5,"user_character_id": null,"character_type": 1,"versus_child_character_id": null},{"position": 6,"user_character_id": null,"character_type": 2,"versus_child_character_id": null},{"position": 7,"user_character_id": null,"character_type": 2,"versus_child_character_id": null},{"position": 8,"user_character_id": null,"character_type": 2,"versus_child_character_id": null}]}]}'
    return deck_str
    
def generate_push_notification_token():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=64))

def suggest_character():
    suggestions = {
        'Chopper': 12760,
        'Marco': 12575,
        'Baggy': 10153,
        'Violet': 1121
    }

    print("Characters:")
    for index, name in enumerate(suggestions.keys(), 1):
        print(f"{index}. {name} ({suggestions[name]})")

    while True:
        try:
            selection = int(input("Enter the corresponding number: "))
            if 1 <= selection <= len(suggestions):
                char_name, char_id = list(suggestions.items())[selection - 1]
                config.select_friend = True
                return char_id
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")




def encrypt_data(data, key):
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(str(data).encode())
    return base64.b64encode(cipher.nonce + tag + ciphertext).decode()

def decrypt_data(encrypted_data, key):
    encrypted_data = base64.b64decode(encrypted_data)
    nonce = encrypted_data[:16]
    tag = encrypted_data[16:32]
    ciphertext = encrypted_data[32:]
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    data = cipher.decrypt_and_verify(ciphertext, tag)
    return eval(data.decode())

def generate_aes_key(key_length=32):
    return secrets.token_bytes(key_length)
