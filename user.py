import asyncio
import json
from colorama import init, Fore, Style, Back
import config
import utils
import cryption
import db
from tqdm import tqdm
from PIL import Image
import io
import asyncio
import aiohttp
import asyncio
import requests
import deck, deck_ship, farm
import sys

# Coloroma autoreset
init(autoreset=True)

card_vwr = deck.CharacterSelector([])
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def user_info():

    url = config.get_version() + "/facilities?skip_errand=true" 
    r = config.session.get(url, headers=config.session.headers)

    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))

    if 'error' not in decoded:
        data = [
            ("Id:", decoded["current_user"]["id"]),
            ("Name:", decoded["current_user"]["nickname"]),
            ("Level:", decoded["current_user"]["level"]),
            ("Gems:", decoded["current_user"]["dpoint"]),
            ("Berry:", decoded["current_user"]["current_money"]),
            ("Stamina:", decoded["current_user"]["stamina"], "/", decoded["current_user"]["max_stamina"]),
            ("Bounty:", decoded["current_user"]["current_bounty"]),
            ("Box space:", decoded["current_user"]["max_character_total"]),
        ]

        output = "\n".join(["{} {}".format(info[0], info[1]) for info in data])
        print(output)
    else:
        print(Fore.RED + Style.BRIGHT + decoded)
        return

def my_data():

    url = config.get_version() + "/users/mydata"

    data1 = '{"fellows_last_update_time":915177600}'
    encoded_data = cryption.Encrypt(config.get_session_key(), data1)
    data2 = {'encoded': True,
             'data': encoded_data.decode('utf-8')}

    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)

    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))
    
    colosseum_group_boss_ids = []

    for id in decoded['current_user_event_opens']:
        colosseum_group_boss_id = id['colosseum_group_boss_id']
        colosseum_group_boss_ids.append(colosseum_group_boss_id)

    return colosseum_group_boss_ids
    
def get_user_character_id(character_id):
    
    url = config.get_version() + '/user_characters.json?page=1'
    r = config.session.get(url, headers=config.session.headers)
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))

    for user_character in decoded["user_characters"]:
        if user_character["character_id"] == character_id:
            return user_character["id"]
    print("Character not found")
    return None

def get_user_ship_id(ship_id):
    
    url = config.get_version() + '/user_ships.json?page=1'
    r = config.session.get(url, headers=config.session.headers)
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))
    
    for user_ships in decoded["user_ships"]:
        if user_ships["ship_id"] == ship_id:
            return user_ships["id"]
    print("Ship not found")
    return None

def change_ship():
    
    print("Fetching ships from servers...")
    
    url = config.get_version() + '/user_ships.json?page=1'
    r = config.session.get(url, headers=config.session.headers)
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))
    user_ships = []
    total_page = decoded['page_total']
    for page in range(1,total_page+1):
        url = config.get_version() + '/user_ships.json?page=' + str(page)
        r = config.session.get(url, headers=config.session.headers)
        decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
        decoded = json.loads(decoded.value.decode('utf-8'))
        for user_ship in decoded["user_ships"]:
            user_ships.append((user_ship["ship_id"], user_ship["level"]))
    
    try:
        db.Model.set_connection_resolver(db.db_glb)
        
        ship_ids = [ship[0] for ship in user_ships]
        ship_levels = [ship[1] for ship in user_ships]
        ship_names = db.ship_name.where_in('serverId_', ship_ids).get()
        ship_lvls = db.ship_level.where_in('shipId_', ship_ids).where_in('level_', ship_levels).get()
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + 'An error occurred:', e)
        return 0
        
    ship_to_diplay = []
    for i in range(len(user_ships)):
        ship_to_diplay.append(f"{ship_names[i].serverId_} - {ship_names[i].name_} | {ship_lvls[i].effectDescription_} | lvl : {ship_lvls[i].level_}")
    deck_ship.show_ship(ship_to_diplay)

def tutorial_init_team():
    
    url = config.get_version() + '/decks/bulk_update'
    data1 = utils.format_deck_json_v1(get_user_ship_id(1), get_user_character_id(2))
    
    encoded_data = cryption.Encrypt(config.get_session_key(), data1)
    data2 = {'encoded': True,
             'data': encoded_data.decode('utf-8')}
    
    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))
    
    if 'status' in decoded:
        if decoded['status'] != 'ok':
            print(Fore.RED + Style.BRIGHT +
                  "error when updating team : " + r.json())
            return None
            
def send_friend_requests(code):
    url = config.get_version() + f'/fellows/search?code={code}'
    r = config.session.get(url, headers=config.session.headers)
    try:
        decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
        decoded = json.loads(decoded.value.decode('utf-8'))
        
        id = decoded['user']['user_id']
        
        url = config.get_version() + f'/users/{id}/fellow_request'
        data1 = '{"sent_from": 101}'
        encoded_data = cryption.Encrypt(config.get_session_key(), data1)
        data2 = {'encoded': True,
                'data': encoded_data.decode('utf-8')}
        r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
        print(Fore.GREEN + Style.BRIGHT + "Done !")
    except KeyError:
        print(Fore.RED + Style.BRIGHT + 'User not found.')
        return 0
    
def accept_friend_requests():
    url = config.get_version() + '/messagings.json?page=1'
    r = config.session.get(url, headers=config.session.headers)
    idfellow= []
    try:
        decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
        decoded = json.loads(decoded.value.decode('utf-8'))
        for request_id in decoded["messagings"]:
            idfellow.append(request_id["receive_fellow_request_id"])
        for ids in idfellow:
            url = config.get_version() + f'/fellow_requests/{ids}/accept'
            data1 = '{"_dummy": "1"}'
            encoded_data = cryption.Encrypt(config.get_session_key(), data1)
            data2 = {'encoded': True,
                        'data': encoded_data.decode('utf-8')}
            r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
            decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
            decoded = json.loads(decoded.value.decode('utf-8'))
    except KeyError:
        print(Fore.RED + Style.BRIGHT + "No friend request.")
        
def fetch_page(page):
    url = config.get_version() + '/user_characters.json?page=' + str(page)
    r = requests.get(url, headers=config.session.headers)
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    return json.loads(decoded.value.decode('utf-8'))

def fetch_all_pages(total_page):
    return [fetch_page(page) for page in range(1, total_page + 1)]

def change_team():
    print("Fetching user cards from servers...")

    url = config.get_version() + '/user_characters.json?page=1'
    r = config.session.get(url, headers=config.session.headers)
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))
    total_page = decoded['page_total']

    pages_data = fetch_all_pages(total_page)
    user_chars = {}
    for page_data in pages_data:
        for user_character in page_data["user_characters"]:
            user_chars[user_character["character_id"]] = user_character["id"]

    print("Connection to database...")
    card_ids = [key for key in user_chars.keys()]
    card_list = []
    for card in card_ids:
        
        try:
            db.Model.set_connection_resolver(db.db_glb)
            db_card = db.characters.where("serverId_", card).first()
        except Exception as e:
            print(Fore.RED + Style.BRIGHT + 'An error occurred:', e)
            return 0
        
        if not db_card:
            continue
        if db_card.limitExp_ == 0:
            continue
        # Get card type
        if db_card.attributeId_ == 1:
            type1 = 'STR'
        elif db_card.attributeId_ == 2:
            type1 = 'DEX'
        elif db_card.attributeId_ == 3:
            type1 = 'QCK'
        elif db_card.attributeId_ == 4:
            type1 = 'PSY'
        elif db_card.attributeId_ == 5:
            type1 = 'INT'
        else:
            type1 = ''
        # Get card type
        if db_card.subAttributeId_ == 1:
            type2 = 'STR'
        elif db_card.subAttributeId_ == 2:
            type2 = 'DEX'
        elif db_card.subAttributeId_ == 3:
            type2 = 'QCK'
        elif db_card.subAttributeId_ == 4:
            type2 = 'PSY'
        elif db_card.subAttributeId_ == 5:
            type2 = 'INT'
        elif db_card.subAttributeId_ == -1:
            type2 = ''
        else:
            type2 = ''
        # Get card class
        if db_card.characterType_ == 1:
            class1 = 'FIGHTER'
        elif db_card.characterType_ == 2:
            class1 = 'SLASHEUR'
        elif db_card.characterType_ == 3:
            class1 = 'STRIKER'
        elif db_card.characterType_ == 4:
            class1 = 'SHOOTER'
        elif db_card.characterType_ == 5:
            class1 = 'FREE SPIRIT'
        elif db_card.characterType_ == 6:
            class1 = 'DRIVEN'
        elif db_card.characterType_ == 7:
            class1 = 'CEREBRAL'
        elif db_card.characterType_ == 8:
            class1 = 'POWERHOUSE'
        elif db_card.characterType_ == -1:
            class1 = '' 
        else:
            class1 = ''    
        # Get card class
        if db_card.subCharacterType_ == 1:
            class2 = 'FIGHTER'
        elif db_card.subCharacterType_ == 2:
            class2 = 'SLASHEUR'
        elif db_card.subCharacterType_ == 3:
            class2 = 'STRIKER'
        elif db_card.subCharacterType_ == 4:
            class2 = 'SHOOTER'
        elif db_card.subCharacterType_ == 5:
            class2 = 'FREE SPIRIT'
        elif db_card.subCharacterType_ == 6:
            class2 = 'DRIVEN'
        elif db_card.subCharacterType_ == 7:
            class2 = 'CEREBRAL'
        elif db_card.subCharacterType_ == 8:
            class2 = 'POWERHOUSE'
        elif db_card.subCharacterType_ == -1:
            class2 = ''     
        else:
            class2 = ''
            
        # Get card rarity
        if db_card.rarity_ == 0:
            rarity = 'Item'
            continue 
        elif db_card.rarity_ == 1:
            rarity = '1★'
            if db_card.isRarityPlus_ == 1:
                rarity = rarity + '+'
        elif db_card.rarity_ == 2:
            rarity = '2★'
            if db_card.isRarityPlus_ == 1:
                rarity = rarity + '+'
        elif db_card.rarity_ == 3:
            rarity = '3★'
            if db_card.isRarityPlus_ == 1:
                rarity = rarity + '+'
        elif db_card.rarity_ == 4:
            rarity = '4★'
            if db_card.isRarityPlus_ == 1:
                rarity = rarity + '+'
        elif db_card.rarity_ == 5:
            rarity = '5★'  
            if db_card.isRarityPlus_ == 1:
                rarity = rarity + '+'
        elif db_card.rarity_ == 6:
            rarity = '6★'     
            if db_card.isRarityPlus_ == 1:
                rarity = rarity + '+'
      
        uniqueID = None
        for key, value in user_chars.items():  
            if key == db_card.serverId_:
                uniqueID = value
        dict = {
            'Type1': type1,
            'Type2': type2,
            'Types': type1 + type2,
            'class1': class1,
            'class2': class2,
            'Classes': class1 + class2,
            'ID': db_card.serverId_,
            'image_url': utils.get_card_url(db_card.serverId_),
            'Rarity': rarity,
            'Name': db_card.name_,
            'UniqueID': uniqueID
        }
        card_list.append(dict)
        
    # Sort cards
    print(Fore.CYAN + Style.BRIGHT + "Sorting cards...")
    card_list = sorted(card_list, key=lambda k: k['Name'])
    card_list = sorted(card_list, key=lambda k: k['Rarity'], reverse=True)
    print(Fore.GREEN + Style.BRIGHT + "Done !")
    # Define cards to display
    loop.run_until_complete(card_vwr.create_gui(card_list))
    ids_list =  config.team
    url = config.get_version() + '/decks/bulk_update'
    
    if config.premium: 
        ship = int(config.ship[0].split()[0])
    else:
        ship = 1
    data1 = utils.format_deck_json(get_user_ship_id(ship), ids_list)
    
    encoded_data = cryption.Encrypt(config.get_session_key(), data1)
    data2 = {'encoded': True,
             'data': encoded_data.decode('utf-8')}
    
    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
    if 'error' in r.json():
        print(Fore.RED + Style.BRIGHT + str(r.json()))
        return 0
    
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))
    if 'status' in decoded:
        if decoded['status'] != 'ok':
            print(Fore.RED + Style.BRIGHT +
                  "error when updating team : " + str(r.json()))
            return None
        
    print(Fore.GREEN + Style.BRIGHT + "Team updated !")
    print("---------------------------------------")
    return 0

def get_messaging_ids():

    user_login_bonuses()
    user_login_stamp()

    url = config.get_version() + '/messagings.json?page=1'
    r = config.session.get(url, headers=config.session.headers)
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))

    if 'error' not in decoded:
        id_list_1 = []
        id_list_2 = []
        ticket_list_gift_id = []
        gift_item_target_id = []
        accepted_tickets_count = 0
        for messaging in decoded["messagings"]:
        
            if messaging['gift_type'] != 'gacha_ticket':
                id_list_1.append(messaging["id"])
            if messaging['gift_type'] != 'gacha_ticket':
                id_list_2.append(messaging["gift_id"])
            if messaging['gift_type'] == 'gacha_ticket':
                ticket_list_gift_id.append(messaging["gift_id"])
                gift_item_target_id.append(messaging["gift_item_target_id"])
        
        if len(ticket_list_gift_id) != 0:
            for idx, gift_id in enumerate(ticket_list_gift_id):
                url = config.get_version() + f"/ticket_gachas/{gift_item_target_id[idx]}/confirm"
                data1 = '{"gift_id":'+ str(gift_id) + ',' + '"total": 1' + '}'
                
                encoded_data = cryption.Encrypt(config.get_session_key(), data1)
                data2 = {'encoded': True, 'data': encoded_data.decode('utf-8')}
                r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
                decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
                decoded = json.loads(decoded.value.decode('utf-8'))
                
                transaction = decoded['transaction_id']
                
                url =  config.get_version() + f"/ticket_gachas/{gift_item_target_id[idx]}/execute"
                data1 = '{"gift_id":'+ str(gift_id) + ',' + '"total": 1,' + '"transaction_id":' + str(transaction) + '}'
                encoded_data = cryption.Encrypt(config.get_session_key(), data1)
                data2 = {'encoded': True, 'data': encoded_data.decode('utf-8')}
                r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
                decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
                decoded = json.loads(decoded.value.decode('utf-8'))
                accepted_tickets_count += 1

        url = config.get_version() + '/messagings/received'
        data1 = '{"messaging_ids":'+ str(id_list_1) + '}'
        
        encoded_data = cryption.Encrypt(config.get_session_key(), data1)
        data2 = {'encoded': True, 'data': encoded_data.decode('utf-8')}
        r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
        if 'error' not in r.json():
            decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
            decoded = json.loads(decoded.value.decode('utf-8'))
            print(f"Number of accepted tickets: {accepted_tickets_count}")
            return id_list_2
        else:
            print(Fore.RED + Style.BRIGHT + "Error occured retrying..")
            accept_gifts()
    else:
        print(Fore.RED + Style.BRIGHT + decoded)
        return

def accept_gifts():

    try:
        gifts = get_messaging_ids()
        gifts = [x for x in gifts if x is not None]
    except TypeError:
        accept_gifts()
    try:
        if len(gifts) == 0:
            return 0
    except TypeError:
        accept_gifts()
  
    url = config.get_version() + "/gifts/bulk_receive"
    data1 = '{"gift_ids":'+ str(gifts) +'}'

    encoded_data = cryption.Encrypt(config.get_session_key(), data1)
    
    data2 = {'encoded': True,
             'data': encoded_data.decode('utf-8')}
    
    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)


    if 'error' not in r.json():
        decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
        decoded = json.loads(decoded.value.decode('utf-8'))
        print(Fore.GREEN + Style.BRIGHT + 'Gifts Accepted...')
    else:
        print(Fore.RED + Style.BRIGHT + str(r.json()))
        accept_gifts()
        return

def invitations():
    try:
        code = int(input(Style.BRIGHT + "Enter user invitation code : ").strip())
        
        data1 = '{' + f'"invitation_code": "{code}"' +'}'
        encoded_data = cryption.Encrypt(config.get_session_key(), data1)
        
        data2 = {'encoded': True,
                'data': encoded_data.decode('utf-8')}
        
        url = config.get_version() + '/invitations/confirm'
        r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
        decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
        decoded = json.loads(decoded.value.decode('utf-8'))
        if 'error_message' in decoded:
            print(Fore.RED + Style.BRIGHT + decoded)
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + str(r.json()))
        return
        
    return 

def user_errands():

    stage_id = []
    error_id = []
    page = 1

    while True:

        url = config.get_version() + '/user_quest_libraries?page=' + str(page)
        r = config.session.get(url, headers=config.session.headers)

        decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
        decoded = json.loads(decoded.value.decode('utf-8'))
        
        if 'error' not in decoded:
            for id in decoded["user_quest_libraries"]:
                if id["clear_counter"] == 0:
                    error_id.append(id["quest_id"])
                else:
                    stage_id.append(id["quest_id"])
        else:
            print(Fore.RED + Style.BRIGHT + decoded)
            return
        if page == decoded["page_total"]:
            break
        else:
            page += 1

    return stage_id

def actRefill():
    #check items
    url = config.get_version() + '/user_items/stamina_recover_meats'
    r = config.session.get(url, headers=config.session.headers)

    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))
    if config.toggle_meat == True:
        for item in decoded['user_stamina_recover_meat_items']:
            if item["quantity"] > 0:
                items = item["item_id"]
                url = config.get_version() + '/stamina_recoveries/execute_by_meat'
                
                data1 = '{"items":[{"item_id":' + str(items) + ',"quantity":1}]}'

                encoded_data = cryption.Encrypt(config.get_session_key(), data1)
                data2 = {'encoded': True,
                        'data': encoded_data.decode('utf-8')}
                
                r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
                decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
                decoded = json.loads(decoded.value.decode('utf-8'))
                print(Fore.GREEN + Style.BRIGHT + 'STAMINA RESTORED WITH ITEM !')
                return
            else:
                print(Fore.RED + Style.BRIGHT +"No meat to refill stamina !")
                return
    else:
        #check stones
        url = config.get_version() + "/facilities?skip_errand=true" 
        r = config.session.get(url, headers=config.session.headers)
        decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
        decoded = json.loads(decoded.value.decode('utf-8'))
        if decoded["current_user"]["dpoint"] > 0:
            url = config.get_version() + '/stamina_recoveries/confirm'
            
            r = config.session.get(url, headers=config.session.headers)
            decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
            decoded = json.loads(decoded.value.decode('utf-8'))
            transaction_id = None
            if 'transaction_id' in decoded:
                transaction_id = decoded['transaction_id']
            else:
                print(Fore.RED + Style.BRIGHT + decoded)
                return 
        
            data1 = '{' + f'"transaction_id": {transaction_id}' +'}'
            encoded_data = cryption.Encrypt(config.get_session_key(), data1)
            data2 = {'encoded': True,
                    'data': encoded_data.decode('utf-8')}
            
            url = config.get_version() + '/stamina_recoveries/execute'
            r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
            decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
            decoded = json.loads(decoded.value.decode('utf-8'))
            print(Fore.GREEN + Style.BRIGHT + 'STAMINA RESTORED WITH GEMS !')
            return
        else:
            print(Fore.RED + Style.BRIGHT +"No gems to refill stamina !")
            return
            
def get_friend():
    
    url = config.get_version() + '/adventurers'
    r = config.session.get(url, headers=config.session.headers)
    
    if 'error' not in r.json():
        decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
        decoded = json.loads(decoded.value.decode('utf-8'))
        
        match_found = False
        
        if config.random_friend:
            for adventurer in decoded["adventurers"]:
                if len(adventurer["user_character"]["child_characters"]) == 0 :
                    match_found = True
                    skill_keys = [key for key in adventurer["user_character"] if key.startswith("option_skill") or key.startswith("potential_skill")]
                    skill_keys.append("level_limit_break_composition_count")

                    # Pour chaque clé, vérifier la valeur et la stocker si elle n'est pas None
                    skills = {}
                    for key in skill_keys:
                        value = adventurer["user_character"][key]
                        if value is not str('Null'):
                            skills[key] = value
                    json_skills = json.dumps(skills)
                    json_skills = json_skills.strip("{}")

                    data = {
                        "id":adventurer["user_id"],
                        "main_deck":True,
                        "character_id":adventurer["user_character"]["character_id"],
                        "level":adventurer["user_character"]["level"],
                        "skill_level":adventurer["user_character"]["skill_level"],
                        "plus_stamina":adventurer["user_character"]["plus_stamina"],
                        "plus_attack":adventurer["user_character"]["plus_attack"],
                        "plus_healing":adventurer["user_character"]["plus_healing"],
                        "limit_break_sequence":adventurer["user_character"]["limit_break_sequence"]
                        }
                    data = json.dumps(data)
                    data= data.strip("{}")
                    return data + ', ' + json_skills
        else:
            friends = []
            for adventurer in decoded["adventurers"]:
                friends.append(adventurer["user_character"]["character_id"])
            db.Model.set_connection_resolver(db.db_glb)
            db_card = db.characters.where_in("serverId_", friends).get()
            friends.clear()
            for character in db_card:   
                    if character.attributeId_ == 1:
                        type1 = '[STR]'
                    elif character.attributeId_ == 2:
                        type1 = '[DEX]'
                    elif character.attributeId_ == 3:
                        type1 = '[QCK]'
                    elif character.attributeId_ == 4:
                        type1 = '[PSY]'
                    elif character.attributeId_ == 5:
                        type1 = '[INT]'
                        
                    if character.rarity_ == 0:
                        rarity = '0'
                    elif character.rarity_ == 1:
                        rarity = '1'
                    elif character.rarity_ == 2:
                        rarity = '2'
                    elif character.rarity_ == 3:
                        rarity = '3'
                    elif character.rarity_ == 4:
                        rarity = '4'
                    elif character.rarity_ == 5:
                        rarity = '5'  
                    elif character.rarity_ == 6:
                        rarity = '6'  
                    
                    if character.subName_ != "":
                        subname =  character.subName_
                    else:
                        subname = ""
                    
                    data_dict = {
                        'Type1': type1,
                        'Rarity': rarity,
                        'Name': character.name_,
                        'SubName': subname
                    }
                    friends.append(data_dict)
                # create a list to store the output
            output_list = []
            for i, value in enumerate(friends):
                output_list.append(Style.BRIGHT + str(i) + ' | ' + value['Name'] + " (" + value['SubName'] + ") " + value['Type1']+ " | " + "Rarity : "+ value['Rarity']+"★")
                
            for e in output_list:
                    print(e)
                    
            select = input("\nEnter a number to select a friend leader, or 'refresh' to refresh : ")
            if select.isdigit():
                match_found = True
                select = int(select)
                adventurer = decoded["adventurers"][select]
                skill_keys = [key for key in adventurer["user_character"] if key.startswith("option_skill") or key.startswith("potential_skill")]
                skill_keys.append("level_limit_break_composition_count")

                    # Pour chaque clé, vérifier la valeur et la stocker si elle n'est pas None
                skills = {}
                for key in skill_keys:
                        value = adventurer["user_character"][key]
                        if value is not str('Null'):
                            skills[key] = value
                json_skills = json.dumps(skills)
                json_skills = json_skills.strip("{}")

                data = {
                        "id":adventurer["user_id"],
                        "main_deck":True,
                        "character_id":adventurer["user_character"]["character_id"],
                        "level":adventurer["user_character"]["level"],
                        "skill_level":adventurer["user_character"]["skill_level"],
                        "plus_stamina":adventurer["user_character"]["plus_stamina"],
                        "plus_attack":adventurer["user_character"]["plus_attack"],
                        "plus_healing":adventurer["user_character"]["plus_healing"],
                        "limit_break_sequence":adventurer["user_character"]["limit_break_sequence"]
                        }
                data = json.dumps(data)
                data= data.strip("{}")
                return data + ', ' + json_skills
            
        if not match_found:
            get_friend()
    else:
        print(Fore.RED + Style.BRIGHT + r.json())
        return

def user_login_bonuses():
    headers = {
        'Host': config.get_host(),
        'Content-type': 'application/json',
        'X-SESSION': config.sakura_session,
        'Accept': 'application/json',
        'User-Agent': config.get_user_agent(),
        'Authorization': 'Basic c2FrdXJhOjBubHkwbmU=',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'close'
        }
    url = config.get_version() + '/users/total_login_bonus'
    r = config.session.get(url, headers=config.session.headers)
    
def user_login_stamp():
    headers = {
        'Host': config.get_host(),
        'Content-type': 'application/json',
        'X-SESSION': config.sakura_session,
        'Accept': 'application/json',
        'User-Agent': config.get_user_agent(),
        'Authorization': 'Basic c2FrdXJhOjBubHkwbmU=',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'close'
        }
    url = config.get_version() + '/user_login_stamp_campaigns/execute'
    data1 = '{ "_dummy": "1" }'
    encoded_data = cryption.Encrypt(config.get_session_key(), data1)
    data2 = {'encoded': True,
             'data': encoded_data.decode('utf-8')}
    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))
    config.username = decoded["current_user"]["nickname"]   
    
def change_nickname():
    headers = {
            'Host': config.get_host(),
            'Content-type': 'application/json',
            'X-SESSION': config.sakura_session,
            'Accept': 'application/json',
            'User-Agent': config.get_user_agent(),
            'Authorization': 'Basic c2FrdXJhOjBubHkwbmU=',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'close'
            }
    nickname = input(Style.BRIGHT + "Enter nickname: ").strip()
    url = config.get_version() + '/users'
    data1 = '{' + f'"nickname": "{nickname}"' +'}'
    encoded_data = cryption.Encrypt(config.get_session_key(), data1)
    data2 = {'encoded': True,
                'data': encoded_data.decode('utf-8')}
    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))
    
    if 'status' not in decoded:
            print(Fore.RED + Style.BRIGHT +
                  "error when sending nickname : " + str(decoded))
    else:
        print(Style.BRIGHT + "Nickname changed for : " + nickname)
    return
    
def get_user_point():
    
    headers = {
            'Host': config.get_host(),
            'Content-type': 'application/json',
            'X-SESSION': config.sakura_session,
            'Accept': 'application/json',
            'User-Agent': config.get_user_agent(),
            'Authorization': 'Basic c2FrdXJhOjBubHkwbmU=',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'close'
            }
    url = config.get_version() + '/event_opens/user_info'
    r = config.session.get(url, headers=config.session.headers)
    try:
        decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
        decoded = json.loads(decoded.value.decode('utf-8'))
    except KeyError:
        print(Fore.RED + Style.BRIGHT + str(r.json()))
        return 0
        
    return{
        'items': decoded['user_event_open_recover_item_num'],
        'points': decoded['current_event_open_point']
        }

def get_rank():
    url = config.get_version() + '/bounty_rankings/user_around'
    r = config.session.get(url, headers=config.session.headers)
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))
    print(decoded)
    print(Style.BRIGHT + '---------------------------------')
    
def check_box_limit():
    url = config.get_version() + "/facilities?skip_errand=true" 
    r = config.session.get(url, headers=config.session.headers)

    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))

    if 'error' not in decoded:
        limit = decoded["current_user"]["max_character_total"]
        chars = 0
    else:
        print(Fore.RED + Style.BRIGHT + str(r.json()))
        return
    
    url = config.get_version() + '/user_characters.json?page=1'
    r = config.session.get(url, headers=config.session.headers)
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))
    total_page = decoded['page_total']
    
    for page in range(1,total_page+1):
        url = config.get_version() + '/user_characters.json?page=' + str(page)
        r = config.session.get(url, headers=config.session.headers)
        decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
        decoded = json.loads(decoded.value.decode('utf-8'))
        chars += len(decoded["user_characters"])
    
    config.user_characters_nb = chars
    config.box_limit = limit
    if chars >= limit:
        return True
    else:
        return False

async def download_image(session, url):
    async with session.get(url) as response:
        return await response.read()

async def generate_box_banner(images, num_chars_per_image=80):
    num_images = (len(images) + num_chars_per_image - 1) // num_chars_per_image
    img_width = 112
    img_height = 112
    padding = 4

    async with aiohttp.ClientSession() as session:
        for i in range(num_images):
            start_idx = i * num_chars_per_image
            end_idx = min(start_idx + num_chars_per_image, len(images))
            num_chars = end_idx - start_idx
            
            num_cols = (num_chars + 6) // 7
            banner_width = num_cols * (img_width + padding) - padding
            banner_height = (num_chars + num_cols - 1) // num_cols * (img_height + padding) - padding
            
            banner = Image.new('RGBA', (banner_width, banner_height), (255, 255, 255, 255))
            
            tasks = [download_image(session, img_url) for img_url in images[start_idx:end_idx]]
            images_data = await asyncio.gather(*tasks)

            for j, img_data in enumerate(images_data):
                row = j // num_cols
                col = j % num_cols
                x = col * (img_width + padding)
                y = row * (img_height + padding)
                
                img = Image.open(io.BytesIO(img_data)).convert('RGBA')
                img = img.resize((img_width, img_height), resample=Image.BOX)
                banner.paste(img, (x, y), img)
            
            banner.save(f'banner_{i}.png')
            banner.show()
            if config.premium:
                # banner.save('summon.png')
                # webhook code here
                pass
    return
                            
def box_banner():
    print("Fetching user cards from servers...")

    url = config.get_version() + '/user_characters.json?page=1'
    r = config.session.get(url, headers=config.session.headers)
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))

    total_page = decoded['page_total']
    pages_data = fetch_all_pages(total_page)

    characters = []
    db.Model.set_connection_resolver(db.db_glb)
    db_card = db.characters.where("rarity_", '>=', 5).get()
    db_car_ids = [x.serverId_ for x in db_card]

    for page_data in pages_data:
        for character in page_data["user_characters"]:
            try:
                max_exp = character['max_exp']
                if max_exp <= 0:
                    continue
                characters.append({
                    'character_id': character['character_id'],
                    'available_exp_for_composition': character['available_exp_for_composition']
                })
            except KeyError:
                pass

    characters = sorted(characters, key=lambda x: x['character_id'], reverse=True)
    images = [f"https://cdn.gb.onepiece-tc.jp/en/images/characters/character_{str(char['character_id']).zfill(4)}_t.png" for char in characters if char['character_id'] in db_car_ids]

    if len(images) == 0:
        print('No character to display')
        return

    asyncio.run(generate_box_banner(images))
    return

def trailactRefill():
    

    #check items
    url = config.get_version() + '/user_items/stamina_recover_meats'
    r = config.session.get(url, headers=config.session.headers)

    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))

    for item in decoded['user_stamina_recover_meat_items']:
        if item["quantity"] > 0:
            items = item["item_id"]
           
            url = config.get_version() + '/trail_event_stamina_recoveries/execute'
            
            data1 = '{"items":[{"item_id":' + str(items) + ',"quantity":1}]}'

            encoded_data = cryption.Encrypt(config.get_session_key(), data1)
            data2 = {'encoded': True,
                    'data': encoded_data.decode('utf-8')}
            
            r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
            decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
            decoded = json.loads(decoded.value.decode('utf-8'))
            print(Fore.GREEN + Style.BRIGHT + 'PKA STAMINA RESTORED !')




def get_trail_events():
    #1
    url = config.get_version() + '/trail_event'
    r =  config.session.get(url, headers=config.session.headers)
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))
    on_adventure = decoded['on_adventure']
    stamina = decoded['stamina']
    daily_stamina_recovery_count = decoded['daily_stamina_recovery_count']

    if on_adventure == False:
        url = config.get_version() + '/trail_event/map'
        data1 = '{"_dummy": "1"}'
        encoded_data = cryption.Encrypt(config.get_session_key(), data1)
        data2 = {'encoded': True,
                            'data': encoded_data.decode('utf-8')}
        r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
    
    if stamina == 0:
        if daily_stamina_recovery_count < 2:
            trailactRefill()
        else:
            print(Fore.RED+ Style.BRIGHT + "No stamina to start PKA event.")
            return 0
            
    else:
        #3
        url = config.get_version() + '/user_trail_event_grids?page=1'
        r = requests.get(url, headers=config.session.headers)
        decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
        decoded = json.loads(decoded.value.decode('utf-8'))

        position_of_different_reward = None
        max_level = 0
        max_level_index = None
        has_quest_levels = False
        previous_x = None
        user_trail_event_grids = decoded.get('user_trail_event_grids', [])
        for i, grid in enumerate(user_trail_event_grids):
            x = grid["position_x"]
            y = grid["position_y"]
            quest_levels = grid["quest_levels"]
            arrived = grid["arrived"]
            finished = grid["finished"]
            battle_finished = grid["battle_finished"]
            trail_grid_id = grid["trail_grid_id"]
            pirates_opponent = grid["pirates_opponent"]
            if previous_x is None or x > previous_x:
                if not has_quest_levels and quest_levels:
                    max_level = max(quest_levels)
                    max_level_index = quest_levels.index(max_level)
                    has_quest_levels = True

                if not quest_levels:
                    if not arrived:
                        url = config.get_version() + f'/user_trail_event_grids/{x},{y}/arrive'
                        print(Fore.YELLOW + Style.BRIGHT + f"Moving to location: {x},{y}")
                        data1 = '{"_dummy": "1"}'
                        encoded_data = cryption.Encrypt(config.get_session_key(), data1)
                        data2 = {'encoded': True, 'data': encoded_data.decode('utf-8')}
                        r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)

                        decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
                        decoded = json.loads(decoded.value.decode('utf-8'))
                        rewards = decoded["user_trail_event_grid"]["rewards"]
                        
                        for index, reward in enumerate(rewards):
                            content_type = reward["content_type"]
                            if content_type != "TrailCharacterEvent":
                                position_of_different_reward = index
                                get_trail_events()

                    if pirates_opponent != None and battle_finished == False:
                                        
                            code = grid["pirates_opponent"]["user_code"]
                            autoteam(stage_id=None,pui=True,pvp=True)
                            print('Begin stage: ID :',code)
                            #start pvp match in pka
                            url = config.get_version() + "/trail_event_pirates_arena_battles/start"
                            data = '{"user_code":"' f"{code}"'","activate_deck_position": 1}'
                            encoded_data = cryption.Encrypt(config.get_session_key(), data)
                            data_encode = {'encoded': True, 'data': encoded_data.decode('utf-8')}
                            r = config.session.post(url, data=json.dumps(data_encode), headers=config.session.headers)
                            decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
                            decoded = json.loads(decoded.value.decode('utf-8'))
                            user_pirates_arena_battle_id = decoded["user_pirates_arena_battle_id"]

                            #execute pvp match in pka
                            url = config.get_version() + "/trail_event_pirates_arena_battles/execute"
                        
                            data = '{"user_pirates_arena_battle_id":"'f"{user_pirates_arena_battle_id}"'"}'
                            encoded_data = cryption.Encrypt(config.get_session_key(), data)
                            data_encode = {'encoded': True, 'data': encoded_data.decode('utf-8')}
                            r = config.session.post(url, data=json.dumps(data_encode), headers=config.session.headers)
                            decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
                            decoded = json.loads(decoded.value.decode('utf-8'))
                        
                            #finish pvp match in pka
                            url = config.get_version() + '/trail_event_pirates_arena_battles/finish'
                            data1 = '{"user_pirates_arena_battle_id":'f'{user_pirates_arena_battle_id}'',"result_type": 1,"ally_dead_character_ids": [],"enemy_dead_character_ids": [],"ally_characters": [],"enemy_characters": [],"ally_leader_character": {"character_id": -1,"health_buff": 0,"attack_buff": 0,"regeneration_buff": 0,"armor_buff": 0,"speed_buff": 0,"skill_accumulate_buff": 0,"knockback_buff": 0,"guard_buff": 0,"critical_buff": 0,"miss_buff": 0,"base_health": 0,"base_attack": 0,"base_regeneration": 0,"base_armor": 0,"base_speed": 0,"base_skill_interval": null},"enemy_leader_character": {"character_id": -1,"health_buff": 0,"attack_buff": 0,"regeneration_buff": 0,"armor_buff": 0,"speed_buff": 0,"skill_accumulate_buff": 0,"knockback_buff": 0,"guard_buff": 0,"critical_buff": 0,"miss_buff": 0,"base_health": 0,"base_attack": 0,"base_regeneration": 0,"base_armor": 0,"base_speed": 0,"base_skill_interval": null},"burst_gauge_json": {"ally_leader_battle_log": {"limit": 0,"critical_count": 0,"guard_count": 0,"knockback_count": 0,"knockout_ally_count": 0,"knockout_enemy_count": 0,"give_damage_count": 0,"receive_damage_count": 0,"give_healing_count": 0,"receive_healing_count": 0,"leader_skill_turn_count": 0,"give_damage_value": 0,"receive_damage_value": 0,"receive_healing_value_ally": 0,"receive_healing_value_enemy": 0,"give_normal_attack_count": 0,"give_heavy_attack_count": 0,"give_full_attack_count": 0,"healing_action_count": 0,"give_abnormal_state_count": 0,"receive_abnormal_state_count": 0,"active_skill_ally_count": 0,"active_skill_enemy_count": 0,"burst_activation_timings": []},"enemy_leader_battle_log": {"limit": 0,"critical_count": 0,"guard_count": 0,"knockback_count": 0,"knockout_ally_count": 0,"knockout_enemy_count": 0,"give_damage_count": 0,"receive_damage_count": 0,"give_healing_count": 0,"receive_healing_count": 0,"leader_skill_turn_count": 0,"give_damage_value": 0,"receive_damage_value": 0,"receive_healing_value_ally": 0,"receive_healing_value_enemy": 0,"give_normal_attack_count": 0,"give_heavy_attack_count": 0,"give_full_attack_count": 0,"healing_action_count": 0,"give_abnormal_state_count": 0,"receive_abnormal_state_count": 0,"active_skill_ally_count": 0,"active_skill_enemy_count": 0,"burst_activation_timings": []' + '}' + '}' + ',"skip": false}'
                            encoded_data = cryption.Encrypt(config.get_session_key(), data1)
                            data2 = {'encoded': True,
                                        'data': encoded_data.decode('utf-8')}
                            r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
                            decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
                            decoded = json.loads(decoded.value.decode('utf-8'))

                            print(Fore.GREEN + Style.BRIGHT + 'Completed stage ' + 'ID: ' + code )
                            url = config.get_version() + f'/user_trail_event_grids/{x},{y}/finish_pirates_arena'
                            data1 = '{"_dummy": "1"}'
                            encoded_data = cryption.Encrypt(config.get_session_key(), data1)
                            data2 = {'encoded': True,
                                        'data': encoded_data.decode('utf-8')}
                            r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
                            decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
                            decoded = json.loads(decoded.value.decode('utf-8'))

                            url = config.get_version() + f'/user_trail_event_grids/{x},{y}/finish'

                            if not finished:
                                    
                                url = config.get_version() + f'/user_trail_event_grids/{x},{y}/finish'
                            
                                if position_of_different_reward is not None:
                                    print("position_of_different_reward: ",position_of_different_reward)
                                    data1 = '{"reward_indices": ['f"{position_of_different_reward}"']}'
                                    encoded_data = cryption.Encrypt(config.get_session_key(), data1)
                                    data_encode = {'encoded': True, 'data': encoded_data.decode('utf-8')}
                                    r = config.session.post(url, data=json.dumps(data_encode), headers=config.session.headers)
                                    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
                                    decoded = json.loads(decoded.value.decode('utf-8'))
                                    get_trail_events()
                                else:
                                    data1 = '{"reward_indices": [0]}'
                                    data3 = '{"reward_indices": [1]}'
                                    data4 = '{"_dummy": "1"}'
                                    data5 = '{"reward_indices": [2]}'
                                    data6 = '{"reward_indices": [0,1]}'
                                    data7 = '{"reward_indices": [0,1,2]}'

                                encoded_data = cryption.Encrypt(config.get_session_key(), data1)
                                data2 = {'encoded': True, 'data': encoded_data.decode('utf-8')}
                                r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
                                
                                try:
                                    encoded_data = cryption.Encrypt(config.get_session_key(), data1)
                                    data2 = {'encoded': True, 'data': encoded_data.decode('utf-8')}
                                    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
                                    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
                                    decoded = json.loads(decoded.value.decode('utf-8'))
                                    
                                except KeyError:
                                    encoded_data = cryption.Encrypt(config.get_session_key(), data3)
                                    data2 = {'encoded': True, 'data': encoded_data.decode('utf-8')}
                                    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
                                
                                    encoded_data = cryption.Encrypt(config.get_session_key(), data4)
                                    data2 = {'encoded': True, 'data': encoded_data.decode('utf-8')}
                                    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
                                
                                    encoded_data = cryption.Encrypt(config.get_session_key(), data5)
                                    data2 = {'encoded': True, 'data': encoded_data.decode('utf-8')}
                                    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)

                                    encoded_data = cryption.Encrypt(config.get_session_key(), data6)
                                    data2 = {'encoded': True, 'data': encoded_data.decode('utf-8')}
                                    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)

                                    encoded_data = cryption.Encrypt(config.get_session_key(), data7)
                                    data2 = {'encoded': True, 'data': encoded_data.decode('utf-8')}
                                    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)

                    if not finished:
                        url = config.get_version() + f'/user_trail_event_grids/{x},{y}/finish'
                        if position_of_different_reward is not None:
                            data1 = '{"reward_indices": ['f"{position_of_different_reward}"']}'
                        else:
                            data1 = '{"reward_indices": [0]}'
                            data3 = '{"reward_indices": [1]}'
                            data4 = '{"_dummy": "1"}'
                            data5 = '{"reward_indices": [2]}'
                            data6 = '{"reward_indices": [0,1]}'
                            data7 = '{"reward_indices": [0,1,2]}'
                        try:
                            encoded_data = cryption.Encrypt(config.get_session_key(), data1)
                            data2 = {'encoded': True, 'data': encoded_data.decode('utf-8')}
                            r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
                            decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
                            decoded = json.loads(decoded.value.decode('utf-8'))
                            
                        except KeyError:
                            encoded_data = cryption.Encrypt(config.get_session_key(), data3)
                            data2 = {'encoded': True, 'data': encoded_data.decode('utf-8')}
                            r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
                        
                            encoded_data = cryption.Encrypt(config.get_session_key(), data4)
                            data2 = {'encoded': True, 'data': encoded_data.decode('utf-8')}
                            r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
                        
                            encoded_data = cryption.Encrypt(config.get_session_key(), data5)
                            data2 = {'encoded': True, 'data': encoded_data.decode('utf-8')}
                            r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
                            
                            encoded_data = cryption.Encrypt(config.get_session_key(), data6)
                            data2 = {'encoded': True, 'data': encoded_data.decode('utf-8')}
                            r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)

                            encoded_data = cryption.Encrypt(config.get_session_key(), data7)
                            data2 = {'encoded': True, 'data': encoded_data.decode('utf-8')}
                            r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
                else:
                    if not arrived:
                        print(Fore.YELLOW + Style.BRIGHT + f"Moving to location: {x},{y}")
                        url = config.get_version() + f'/user_trail_event_grids/{x},{y}/arrive'
                    
                        data1 = '{"_dummy": "1"}'
                        encoded_data = cryption.Encrypt(config.get_session_key(), data1)
                        data2 = {'encoded': True,
                                'data': encoded_data.decode('utf-8')}
                        r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
                        
                        decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
                        decoded = json.loads(decoded.value.decode('utf-8'))
                        
                        quest_levels = decoded["user_trail_event_grid"]["quest_levels"]
                        max_level = max(quest_levels)
                        max_level_index = quest_levels.index(max_level)
                        get_trail_events()
                    
                    if not battle_finished:
                        url = config.get_version() + f'/user_trail_event_grids/{x},{y}/start_quest'
                    
                        data1 = '{"quest_level_index":'f"{max_level_index}"'}'
                        encoded_data = cryption.Encrypt(config.get_session_key(), data1)
                        data2 = {'encoded': True,
                                'data': encoded_data.decode('utf-8')}
                        r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)

                        db.Model.set_connection_resolver(db.db_glb)
                        quest = db.trials_quests.where("serverId_", trail_grid_id).first()

                        farm.complete_stage(str(quest.questId_),trail=True)

                        url = config.get_version() + f'/user_trail_event_grids/{x},{y}/finish_quest'
                    
                        data1 = '{"_dummy": "1"}'
                        encoded_data = cryption.Encrypt(config.get_session_key(), data1)
                        data2 = {'encoded': True,
                                'data': encoded_data.decode('utf-8')}
                        
                        r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
                        decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
                        decoded = json.loads(decoded.value.decode('utf-8'))
                        
                        get_trail_events()
                    if not finished:
                        if i == len(decoded["user_trail_event_grids"]) - 1:
                            url = config.get_version() + f'/user_trail_event_grids/{x},{y}/finish'
                    
                            data1 = '{"_dummy": 1}'
                    
                            encoded_data = cryption.Encrypt(config.get_session_key(), data1)
                            data2 = {'encoded': True,
                                    'data': encoded_data.decode('utf-8')}
                            r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
                        
                            decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
                            decoded = json.loads(decoded.value.decode('utf-8'))
                            print(Fore.GREEN + Style.BRIGHT + f"finished LVL: {max_level}")
                            get_trail_events()
                        else:
                            url = config.get_version() + f'/user_trail_event_grids/{x},{y}/finish'
                        
                            data1 = '{"reward_indices": [0]}'

                            encoded_data = cryption.Encrypt(config.get_session_key(), data1)
                            data2 = {'encoded': True,
                                    'data': encoded_data.decode('utf-8')}
                            r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
                            
                            decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
                            decoded = json.loads(decoded.value.decode('utf-8'))
                            print(Fore.GREEN + Style.BRIGHT + f"finished LVL: {max_level}")
                            get_trail_events()

                previous_x = x



def autoteam(stage_id,pui=False,qck=False,psy=False,intel=False,dex=False,pvp=False):
    print("Fetching user cards from servers...")
    url = config.get_version() + '/user_characters.json?page=1'
    r = config.session.get(url, headers=config.session.headers)
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))

    total_page = decoded['page_total']
    pages_data = fetch_all_pages(total_page)

    user_chars = {}
    for page_data in pages_data:
        for user_character in page_data["user_characters"]:
            user_chars[user_character["character_id"]] = user_character["id"]
    
    card_ids = []
    for key, value in user_chars.items():
        card_ids.append(key)

    card_list = []
    for card in card_ids:
        
        try:
            db.Model.set_connection_resolver(db.db_glb)
            db_card = db.characters.where("serverId_", card).first()
        except Exception as e:
            print(Fore.RED + Style.BRIGHT + 'An error occurred:', e)
            return 0
        
        if not db_card:
            continue
        if db_card.limitExp_ == 0:
            continue

        # Get card type
        if db_card.attributeId_ == 1:
            type1 = '[STR]'
        elif db_card.attributeId_ == 2:
            type1 = '[DEX]'
        elif db_card.attributeId_ == 3:
            type1 = '[QCK]'
        elif db_card.attributeId_ == 4:
            type1 = '[PSY]'
        elif db_card.attributeId_ == 5:
            type1 = '[INT]'
        else:
            type1 = ''
        # Get card type
        if db_card.subAttributeId_ == 1:
            type2 = '[STR]'
        elif db_card.subAttributeId_ == 2:
            type2 = '[DEX]'
        elif db_card.subAttributeId_ == 3:
            type2 = '[QCK]'
        elif db_card.subAttributeId_ == 4:
            type2 = '[PSY]'
        elif db_card.subAttributeId_ == 5:
            type2 = '[INT]'
        elif db_card.subAttributeId_ == -1:
            type2 = ''
        else:
            type2 = ''
        # Get card class
        if db_card.characterType_ == 1:
            class1 = '[FIGHTER]'
        elif db_card.characterType_ == 2:
            class1 = '[SLASHEUR]'
        elif db_card.characterType_ == 3:
            class1 = '[STRIKER]'
        elif db_card.characterType_ == 4:
            class1 = '[SHOOTER]'
        elif db_card.characterType_ == 5:
            class1 = '[FREE SPIRIT]'
        elif db_card.characterType_ == 6:
            class1 = '[DRIVEN]'
        elif db_card.characterType_ == 7:
            class1 = '[CEREBRAL]'
        elif db_card.characterType_ == 8:
            class1 = '[POWERHOUSE]'
        elif db_card.characterType_ == -1:
            class1 = '' 
        else:
            class1 = ''    
        # Get card class
        if db_card.subCharacterType_ == 1:
            class2 = '[FIGHTER]'
        elif db_card.subCharacterType_ == 2:
            class2 = '[SLASHEUR]'
        elif db_card.subCharacterType_ == 3:
            class2 = '[STRIKER]'
        elif db_card.subCharacterType_ == 4:
            class2 = '[SHOOTER]'
        elif db_card.subCharacterType_ == 5:
            class2 = '[FREE SPIRIT]'
        elif db_card.subCharacterType_ == 6:
            class2 = '[DRIVEN]'
        elif db_card.subCharacterType_ == 7:
            class2 = '[CEREBRAL]'
        elif db_card.subCharacterType_ == 8:
            class2 = '[POWERHOUSE]'
        elif db_card.subCharacterType_ == -1:
            class2 = ''     
        else:
            class2 = ''
            
        # Get card rarity
        if db_card.rarity_ == 0:
            rarity = 'Item'
            continue 
        elif db_card.rarity_ == 1:
            rarity = '1★'
            if db_card.isRarityPlus_ == 1:
                rarity = rarity + '+'
        elif db_card.rarity_ == 2:
            rarity = '2★'
            if db_card.isRarityPlus_ == 1:
                rarity = rarity + '+'
        elif db_card.rarity_ == 3:
            rarity = '3★'
            if db_card.isRarityPlus_ == 1:
                rarity = rarity + '+'
        elif db_card.rarity_ == 4:
            rarity = '4★'
            if db_card.isRarityPlus_ == 1:
                rarity = rarity + '+'
        elif db_card.rarity_ == 5:
            rarity = '5★'  
            if db_card.isRarityPlus_ == 1:
                rarity = rarity + '+'
        elif db_card.rarity_ == 6:
            rarity = '6★'     
            if db_card.isRarityPlus_ == 1:
                rarity = rarity + '+'
        uniqueID = None
        for key, value in user_chars.items():  
            if key == db_card.serverId_:
                uniqueID = value
        dict = {
            'Type1': type1,
            'Type2': type2,
            'class1': class1,
            'class2': class2,
            'ID': db_card.serverId_,
            'Rarity': rarity,
            'Name': db_card.name_,
            'UniqueID': uniqueID,
            'Group': db_card.groupId_,
            'cost': db_card.cost_
        }
        card_list.append(dict)
    
    
    gv_stage_ids = ['15001', '15002', '15003', '15004', '15005', '15006', '15007', '15008', '15009', '15010', '15012', '15013','15014']

    filtered_cards = []
    selected_group_ids = []  
    str_characters = []
    dex_characters = []
    qck_characters = []
    psy_characters = []
    int_characters = []

    friend = None

    for card in card_list:
        if pui:
            if ('[STR]' in card['Type1'] or '[STR]' in card['Type2']):
                if card['Group'] not in selected_group_ids:
                    str_characters.append(card)
                    selected_group_ids.append(card['Group'])
        if qck:
            if ('[QCK]' in card['Type1'] or '[QCK]' in card['Type2']):
                if card['Group'] not in selected_group_ids:
                    qck_characters.append(card)
                    selected_group_ids.append(card['Group'])
        if dex:
            if ('[DEX]' in card['Type1'] or '[DEX]' in card['Type2']):
                if card['Group'] not in selected_group_ids:
                    dex_characters.append(card)
                    selected_group_ids.append(card['Group'])
        if psy:
            if ('[PSY]' in card['Type1'] or '[PSY]' in card['Type2']):
                if card['Group'] not in selected_group_ids:
                    psy_characters.append(card)
                    selected_group_ids.append(card['Group'])
        if intel:
            if ('[INT]' in card['Type1'] or '[INT]' in card['Type2']):
                if card['Group'] not in selected_group_ids:
                    int_characters.append(card)
                    selected_group_ids.append(card['Group'])
        #gv
        if stage_id == str(15001):
            if ('[PSY]' in card['Type1'] or '[PSY]' in card['Type2']) and ('[CEREBRAL]' in card['class1'] or '[CEREBRAL]' in card['class2']):
                # Vérifier si le groupId de la carte n'est pas déjà sélectionné
                if card['Group'] not in selected_group_ids:
                    filtered_cards.append(card)
                    selected_group_ids.append(card['Group'])
                    friend = 1859
        elif stage_id == str(15002):
            if ('[STR]' in card['Type1'] or '[STR]' in card['Type2']) and ('[FIGHTER]' in card['class1'] or '[FIGHTER]' in card['class2']):
                if card['Group'] not in selected_group_ids:
                    filtered_cards.append(card)
                    selected_group_ids.append(card['Group'])
                    friend = 631
        elif stage_id == str(15003):
            if ('[DEX]' in card['Type1'] or '[DEX]' in card['Type2']) and ('[SLASHEUR]' in card['class1'] or '[SLASHEUR]' in card['class2']):
                if card['Group'] not in selected_group_ids:
                    filtered_cards.append(card)
                    selected_group_ids.append(card['Group'])
                    friend  = 1501
        elif stage_id == str(15004):
            if ('[QCK]' in card['Type1'] or '[QCK]' in card['Type2']) and ('[FREE SPIRIT]' in card['class1'] or '[FREE SPIRIT]' in card['class2'] ):
                if card['Group'] not in selected_group_ids:
                    filtered_cards.append(card)
                    selected_group_ids.append(card['Group'])
                    friend = 12102
        elif stage_id == str(15005):
            if ('[INT]' in card['Type1'] or '[INT]' in card['Type2']) and ('[DRIVEN]' in card['class1'] or '[DRIVEN]' in card['class2']):

                if card['Group'] not in selected_group_ids and card['cost'] <= 40:
                    filtered_cards.append(card)
                    
                    selected_group_ids.append(card['Group'])
                    
                    friend = 10153
        elif stage_id == str(15006):
            if ('[DEX]' in card['Type1'] or '[DEX]' in card['Type2']) and ('[SHOOTER]' in card['class1'] or '[SHOOTER]' in card['class2']):
                if card['Group'] not in selected_group_ids:
                    filtered_cards.append(card)
                    selected_group_ids.append(card['Group'])
                    friend = 1650
                    
        elif stage_id == str(15007):
            if ('[INT]' in card['Type1'] or '[INT]' in card['Type2']) and ('[POWERHOUSE]' in card['class1'] or '[POWERHOUSE]' in card['class2']):
                if card['Group'] not in selected_group_ids:
                    filtered_cards.append(card)
                    selected_group_ids.append(card['Group'])
                    friend = 1736
        elif stage_id == str(15008):
            if ('[INT]' in card['Type1'] or '[INT]' in card['Type2']) and ('[SLASHEUR]' in card['class1'] or '[SLASHEUR]' in card['class2']):
                if card['Group'] not in selected_group_ids:
                    filtered_cards.append(card)
                    selected_group_ids.append(card['Group'])
                    friend = 10742
        elif stage_id == str(15009):
            if ('[INT]' in card['Type1'] or '[INT]' in card['Type2']) and ('[SLASHEUR]' in card['class1'] or '[SLASHEUR]' in card['class2']):
                if card['Group'] not in selected_group_ids:
                    filtered_cards.append(card)
                    selected_group_ids.append(card['Group'])
                    friend = 1901

        elif stage_id == str(15010):
            if ('[DEX]' in card['Type1'] or '[DEX]' in card['Type2']) and ('[CEREBRAL]' in card['class1'] or '[CEREBRAL]' in card['class2']):
                if card['Group'] not in selected_group_ids:
                    filtered_cards.append(card)
                    selected_group_ids.append(card['Group'])
                    friend = 10244
        
        elif stage_id == str(15013):
            if ('[QCK]' in card['Type1'] or '[QCK]' in card['Type2']) and ('[STRIKER]' in card['class1'] or '[STRIKER]' in card['class2']):
                # Vérifier si le groupId de la carte n'est pas déjà sélectionné
                if card['Group'] not in selected_group_ids:
                    filtered_cards.append(card)
                    selected_group_ids.append(card['Group'])
                    friend = 11555
        
        elif stage_id == str(15014):
            if ('[QCK]' in card['Type1'] or '[QCK]' in card['Type2']) and ('[FIGHTER]' in card['class1'] or '[FIGHTER]' in card['class2']) and card['cost'] <= 50:
                # Vérifier si le groupId de la carte n'est pas déjà sélectionné
                if card['Group'] not in selected_group_ids:
                    filtered_cards.append(card)
                    selected_group_ids.append(card['Group'])
                    friend = 10311


        elif stage_id == str(15011):
            friend = 11259
            if '[STR]' in card['Type1'] or '[STR]' in card['Type2']:
                if '[POWERHOUSE]' in card['class1'] or '[POWERHOUSE]' in card['class2']:
                    if card['Group'] not in selected_group_ids:
                        str_characters.append(card)
                        selected_group_ids.append(card['Group'])

            elif '[DEX]' in card['Type1'] or '[DEX]' in card['Type2']:
                if '[POWERHOUSE]' in card['class1'] or '[POWERHOUSE]' in card['class2']:
                    if card['Group'] not in selected_group_ids:
                        dex_characters.append(card)
                        selected_group_ids.append(card['Group'])
            elif '[QCK]' in card['Type1'] or '[QCK]' in card['Type2']:
                if '[POWERHOUSE]' in card['class1'] or '[POWERHOUSE]' in card['class2']:
                    if card['Group'] not in selected_group_ids:
                        qck_characters.append(card)
                        selected_group_ids.append(card['Group'])

            elif '[PSY]' in card['Type1'] or '[PSY]' in card['Type2']:
                if '[POWERHOUSE]' in card['class1'] or '[POWERHOUSE]' in card['class2']:
                    if card['Group'] not in selected_group_ids:
                        psy_characters.append(card)
                        selected_group_ids.append(card['Group'])
            elif '[INT]' in card['Type1'] or '[INT]' in card['Type2']:
                if '[POWERHOUSE]' in card['class1'] or '[POWERHOUSE]' in card['class2']:
                    if card['Group'] not in selected_group_ids:
                        int_characters.append(card)
                        selected_group_ids.append(card['Group'])
                        
        elif stage_id == str(15012):
            if ('[PSY]' in card['Type1'] or '[PSY]' in card['Type2']) and ('[FIGHTER]' in card['class1'] or '[FIGHTER]' in card['class2']):
                # Vérifier si le groupId de la carte n'est pas déjà sélectionné
                if card['Group'] not in selected_group_ids:
                    filtered_cards.append(card)
                    selected_group_ids.append(card['Group'])
                    friend = 13359


    if stage_id == str(15011):
        if not str_characters or not dex_characters or not qck_characters or not psy_characters or not int_characters:
            print(Fore.RED + Style.BRIGHT + "You don't have at least one character of each type.")
            return {
                'data': False,
            }
        else:
            filtered_cards = [str_characters[0], dex_characters[0], qck_characters[0], psy_characters[0], int_characters[0]]
            if len(filtered_cards) < 5:
                print(Fore.RED + Style.BRIGHT + "You don't have at least one character of each type.")
                return {
                    'data': False,
                }
            else:
                unique_ids = [card['UniqueID'] for card in filtered_cards[:5]]
                # Afficher les uniqueID
                ids_list = []
                for unique_id in unique_ids:
                    ids_list.append(unique_id)
    
    if pui:
        if not str_characters:
            print(Fore.RED + Style.BRIGHT + " 1 You don't have at least one character with this type.")
            return {
                'data': False,
            }
        else:
            filtered_cards = [str_characters[0]]

            if len(filtered_cards) < 1:
                print(Fore.RED + Style.BRIGHT + "2 You don't have at least one character with this type.")
                return {
                    'data': False,
                }
            else:
                unique_ids = [card['UniqueID'] for card in filtered_cards[:1]]
                # Afficher les uniqueID
                ids_list = []
                for unique_id in unique_ids:
                    ids_list.append(unique_id)
    if qck:
        if not qck_characters:
            print(Fore.RED + Style.BRIGHT + "You don't have at least one character with this type.")
            return {
                'data': False,
            }
        else:
            filtered_cards = [qck_characters[0]]

            if len(filtered_cards) < 1:
                print(Fore.RED + Style.BRIGHT + "You don't have at least one character with this type.")
                return {
                    'data': False,
                }
            else:
                unique_ids = [card['UniqueID'] for card in filtered_cards[:1]]
                # Afficher les uniqueID
                ids_list = []
                for unique_id in unique_ids:
                    ids_list.append(unique_id)

    if dex:
        if not dex_characters:
            print(Fore.RED + Style.BRIGHT + "You don't have at least one character with this type.")
            return {
                'data': False,
            }
        else:
            filtered_cards = [dex_characters[0]]

            if len(filtered_cards) < 1:
                print(Fore.RED + Style.BRIGHT + "You don't have at least one character with this type.")
                return {
                    'data': False,
                }
            else:
                unique_ids = [card['UniqueID'] for card in filtered_cards[:1]]
                # Afficher les uniqueID
                ids_list = []
                for unique_id in unique_ids:
                    ids_list.append(unique_id)

    if psy:
        if not psy_characters:
            print(Fore.RED + Style.BRIGHT + "You don't have at least one character with this type.")
            return {
                'data': False,
            }
        else:
            filtered_cards = [psy_characters[0]]

            if len(filtered_cards) < 1:
                print(Fore.RED + Style.BRIGHT + "You don't have at least one character with this type.")
                return {
                    'data': False,
                }
            else:
                unique_ids = [card['UniqueID'] for card in filtered_cards[:1]]
                # Afficher les uniqueID
                ids_list = []
                for unique_id in unique_ids:
                    ids_list.append(unique_id)
    if intel:
        if not int_characters:
            print(Fore.RED + Style.BRIGHT + "You don't have at least one character with this type.")
            return {
                'data': False,
            }
        else:
            filtered_cards = [int_characters[0]]
            if len(filtered_cards) < 1:
                print(Fore.RED + Style.BRIGHT + "You don't have at least one character with this type.")
                return {
                    'data': False,
                }
            else:
                unique_ids = [card['UniqueID'] for card in filtered_cards[:1]]
                # Afficher les uniqueID
                ids_list = []
                for unique_id in unique_ids:
                    ids_list.append(unique_id)
    #pvp autoteam
    if pvp:
        if not str_characters:
            print(Fore.RED + Style.BRIGHT + " 1 You don't have at least one character with this type.")
            return {
                'data': False,
            }
        else:
            filtered_cards = [str_characters[0]]

            if len(filtered_cards) < 1:
                print(Fore.RED + Style.BRIGHT + "2 You don't have at least one character with this type.")
                return {
                    'data': False,
                }
            else:
                unique_ids = [card['UniqueID'] for card in filtered_cards[:1]]
                # Afficher les uniqueID
                ids_list = []
                for unique_id in unique_ids:
                    ids_list.append(unique_id)
                    
    if stage_id in gv_stage_ids:
        if len(filtered_cards) < 5:
            print(Fore.RED + Style.BRIGHT + "You don't have enough units that meet the condition.")
            return {
                'data':False,
            }
        else:
            unique_ids = [card['UniqueID'] for card in filtered_cards[:5]]
            # Afficher les uniqueID
            ids_list = []
            for unique_id in unique_ids:
                ids_list.append(unique_id)
    if pvp:
        url = config.get_version() + '/user_pirates_decks/bulk_update'
        data1 = utils.deck_pvp(ids_list)
       
        encoded_data = cryption.Encrypt(config.get_session_key(), data1)
        data2 = {'encoded': True,
                'data': encoded_data.decode('utf-8')}
        
        r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
        decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
        decoded = json.loads(decoded.value.decode('utf-8'))
        if 'status' in decoded:
            if decoded['status'] != 'ok':
                print(Fore.RED + Style.BRIGHT +
                    "error when updating team : " + str(r.json()))
                return None
                
        print(Fore.GREEN + Style.BRIGHT + "Team updated !")
        return 0
        
    url = config.get_version() + '/decks/bulk_update'
    data1 = utils.format_deck_json(get_user_ship_id(1), ids_list)
    
    encoded_data = cryption.Encrypt(config.get_session_key(), data1)
    data2 = {'encoded': True,
             'data': encoded_data.decode('utf-8')}
    
    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))
    if 'status' in decoded:
        if decoded['status'] != 'ok':
            print(Fore.RED + Style.BRIGHT +
                  "error when updating team : " + str(r.json()))
            return None
        
    print(Fore.GREEN + Style.BRIGHT + "Team updated !")
    return {
        'data':True,
        'friends':friend
        }


def reward_gather_island(facility_ids):
    url = config.get_version() + '/facilities/receive'
    data = {"facility_ids": facility_ids}
    encoded_data = cryption.Encrypt(config.get_session_key(), json.dumps(data))
    data2 = {'encoded': True, 'data': encoded_data.decode('utf-8')}
    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
    
    if "error" in r.json():
        print(Fore.RED + Style.BRIGHT + str(r.json()))  # Affichez l'erreur s'il y en a une
    else:
        decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
        decoded = json.loads(decoded.value.decode('utf-8'))
        if decoded['user_facilities'][0]['daily_facility_info'] is not None:
            return True
        else:
            return False

