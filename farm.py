import json
from colorama import init, Fore, Style
import time
import random
import datetime
import pytz
import user, config , auth,save_data,tutorial
import db
import cryption
from collections import *
import sys
import multiprocessing
import asyncio
import aiohttp
import asyncio
import httpx
# Coloroma autoreset
init(autoreset=True)
"""
Class description.
"""
info_count = 0
def complete_stage(stage_id, attempt=0, gv=False, trail=False):
    global info_count
       
    if attempt > 1:
        print(Fore.RED + Style.BRIGHT + 'Maximum attempt exceed, change your team and/or select a friend leader then try again later for this stage.')
        return 0
    elif 0 < attempt <= 1 :
        print(Fore.RED + Style.BRIGHT + f'Failed to execute stage, attempt {attempt}/1...')
    
    try:
        db.Model.set_connection_resolver(db.db_glb)
        quest = db.quest.where("questId_", stage_id).first()
  
        if quest is not None:
            stage_name = quest.questName_

            print('Begin stage: ' + stage_name + ' | ' + 'ID : ' + stage_id)
        else:
            print(Fore.RED + Style.BRIGHT + 'Does this quest exist?')
            return 0

    except Exception as e:
        print(Fore.RED + Style.BRIGHT + 'An error occurred:', e)
        return 0
    
    
    if trail:
        data1 = '{' + '"id":' + str(stage_id) + ',' + '"increased_result_coefficient":1}'
    
    if gv:
        auto_team = user.autoteam(stage_id)
        if auto_team['data']:
            friend = auto_team['friends']
            # Start quest
            data1 = '{' + '"id":' + str(stage_id) + ',' + '"deck_position":' + str(config.deck) + ',' + '"friend_user": {"id": 56095312,"main_deck": true,"character_id":' + str(friend) + ',"level":' + str(99) + ',"skill_level":' + str(1) + ',"plus_stamina": 200,"plus_attack": 200,"plus_healing": 200,"limit_break_sequence":' + str(31) + ',"option_skill_1_id": 1,"option_skill_1_plus": 5,"option_skill_2_id": 2,"option_skill_2_plus": 5,"option_skill_3_id": 3,"option_skill_3_plus": 5,"option_skill_4_id": 4,"option_skill_4_plus": 5,"option_skill_5_id": 5,"option_skill_5_plus": 5,"potential_skill_1_level": 5,"potential_skill_2_level": 5,"potential_skill_3_level": 5,"level_limit_break_composition_count": 0},"increased_result_coefficient":1,"voyage_quest_mission_level":5}'
        else:
            return 0
        
    else:
        if config.select_friend:
            friend = config.friend_id
            db.Model.set_connection_resolver(db.db_glb)
            card_info = db.characters.where("serverId_", str(friend)).first()
            if card_info is not None:
                level = card_info.maxLevel_
                skill_level = card_info.maxOptionSkill_
                if card_info.extensionLimitBreakCount_ == 0:
                    limit_break_sequence = card_info.limitBreakCount_
                else:
                    limit_break_sequence = card_info.extensionLimitBreakCount_
                    
            _friend = '"id": 56095312,"main_deck": true,"character_id":' + str(friend) + ',"level":' + str(level) + ',"skill_level":' + str(skill_level) + ',"plus_stamina": 200,"plus_attack": 200,"plus_healing": 200,"limit_break_sequence":' + str(limit_break_sequence) + ',"option_skill_1_id": 1,"option_skill_1_plus": 5,"option_skill_2_id": 2,"option_skill_2_plus": 5,"option_skill_3_id": 3,"option_skill_3_plus": 5,"option_skill_4_id": 4,"option_skill_4_plus": 5,"option_skill_5_id": 5,"option_skill_5_plus": 5,"potential_skill_1_level": 5,"potential_skill_2_level": 5,"potential_skill_3_level": 5,"level_limit_break_composition_count": 0'

        coef = int(quest.isIncreasedResult_)
        if coef and config.select_friend == False:
            if quest.isIncreasedResult_ == 0:
                data1 = "{"+f'"id":{stage_id},"deck_position":{config.deck},"increased_result_coefficient":{1}'+"}"
            else:
                data1 = "{"+f'"id":{stage_id},"deck_position":{config.deck},"increased_result_coefficient":{2}'+"}"
        elif coef and config.select_friend :
            if quest.isIncreasedResult_ == 0:
                data1 = '{' + f'"id":{stage_id},' + '"deck_position":' + str(config.deck) + ',' + '"friend_user":{' + str(_friend) + '},' + '"increased_result_coefficient":1' + '}'
            else:
                data1 = '{' + f'"id":{stage_id},' + '"deck_position":' + str(config.deck) + ',' + '"friend_user":{' + str(_friend) + '},' + '"increased_result_coefficient":3' + '}'
        elif config.select_friend:
            if quest.isIncreasedResult_ == 0:
                data1 = '{' + f'"id":{stage_id},' + '"deck_position":' + str(config.deck) + ',' + '"friend_user":{' + str(_friend) + '},' + '"increased_result_coefficient":1' + '}'
            else:
                data1 = '{' + f'"id":{stage_id},' + '"deck_position":' + str(config.deck) + ',' + '"friend_user":{' + str(_friend) + '},' + '"increased_result_coefficient":3' + '}'
        elif config.select_friend == False:
            if quest.isIncreasedResult_ == 0:
                data1 = "{"+f'"id":{stage_id},"deck_position":{config.deck},"increased_result_coefficient":{1}'+"}"
            else:
                data1 = "{"+f'"id":{stage_id},"deck_position":{config.deck},"increased_result_coefficient":{2}'+"}"
        
    encoded_data = cryption.Encrypt(config.get_session_key(), data1)
    data2 = {'encoded': True,
             'data': encoded_data.decode('utf-8')}

    url = config.get_version() + '/quests/start'
    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
    
    if "error" in r.json():
        if r.json()['error']['code'] == 41:
            print(Fore.RED + Style.BRIGHT + str(r.json()))
            user.actRefill()
            if gv:
                complete_stage(stage_id,gv=True)
                return 0
            else:
                complete_stage(stage_id)
                return 0
        elif r.json()['error']['code'] == 60:
            print(Fore.RED + Style.BRIGHT + str(r.json()))
            return
        elif r.json()['error']['code'] == 72:
            print(Fore.RED + Style.BRIGHT + str(r.json()))
            return
        else:
            print(Fore.RED + Style.BRIGHT + str(r.json()))
            complete_stage(stage_id, attempt+1)
            return 0
    
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))

    user_quest_id = None
    base_attack = []
    defeat_num = []
    wave_turn = []
    wave_damage = []
    # print(decoded['enemies'])
    if 'user_quest_id' in decoded:
        user_quest_id = decoded['user_quest_id']
        allies = decoded["allies"]
        base_attack = [ally["attack_damage"] for ally in allies]
        
        for enemy in decoded['enemies']:
            if not defeat_num:
                defeat_num.append(len(enemy['characters']))
            else:
                defeat_num.append(defeat_num[-1] + len(enemy['characters']))
                
        for wave in decoded['enemies']:
            wave_turn.append((wave['wave']))
            
        
        total_healths = []
        for wave in decoded['enemies']:
            wave_health = 0
            for character in wave["characters"]:
                wave_health += character["health"]
            total_healths.append(wave_health)
            
    else:
        print(Fore.RED + Style.BRIGHT + decoded)
        return
    
    data1 = "{" + f'"user_quest_id": {user_quest_id}' +"}"
    encoded_data = cryption.Encrypt(config.get_session_key(), data1)
    
    data2 = {'encoded': True,
             'data': encoded_data.decode('utf-8')}
    
    url = config.get_version() + '/quests/execute'
    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
    

    # waiting_time = random.randint(8,12)
    # waiting_time = 0
    # if int(waiting_time) > 0:
    #     for i in range(waiting_time):
    #         progress = (i + 1) / waiting_time
    #         bar = "#" * int(progress * 20)
    #         percent = progress * 100
    #         remaining = waiting_time - (i + 1)
    #         sys.stdout.write(f"[{bar:<20}] {percent:.1f}% - {remaining} sec remaining\r")
    #         sys.stdout.flush()
    #         if progress == 1:
    #             sys.stdout.write('\r' + ' ' * 50 + '\r')
    #             sys.stdout.flush()
    #         time.sleep(1)

    # Finish quest
    if gv:
         data1 = "{" + f'"user_quest_id": {user_quest_id}, "retry_count": {0}, "clear_turn": {5}, "base_attacks": [0,0,0,0,0,0], "kill_count": 0, "auto_used": false, ' + '"battle_log": {' + f'"defeat_num": [], "wave_damage": [],"wave_turn": [],"wave_skill": []' + "}" + "}"
    else:
        data1 = "{" + f'"user_quest_id": {user_quest_id}, "retry_count": {0}, "base_attacks": [0,0,0,0,0,0], "kill_count": 0, "auto_used": false, ' + '"battle_log": {' + f'"defeat_num": [], "wave_damage": [],"wave_turn": [],"wave_skill": []' + "}" + "}"
    
    encoded_data = cryption.Encrypt(config.get_session_key(), data1)
    data2 = {'encoded': True,
             'data': encoded_data.decode('utf-8')}
    
    url = config.get_version() + '/quests/finish'
    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
    
    try:
        decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
        decoded = json.loads(decoded.value.decode('utf-8'))
    except KeyError:
        print(Fore.RED + Style.BRIGHT + str(r.json()))
        complete_stage(stage_id, attempt+1)
        return 0

    #drops
    gems = decoded['available_dpoint']
    berry = decoded['available_money']
    
    for item in decoded['quest_drops']: 
        if 'user_character' in item:
            character_id = item['user_character']['character_id']
            items = []
            items.append(character_id)
            item_counts = Counter(items)
            config.user_characters_nb += len(item_counts)
            
            for item,count in item_counts.items():
                try:
                    db.Model.set_connection_resolver(db.db_glb)
                    items_id = db.characters.where("serverId_",item).first()
                    if items_id is not None:
                        items_name = items_id.name_
                        if config.select_friend == False:
                            if quest.isIncreasedResult_ == 0:
                                print(Fore.MAGENTA + Style.BRIGHT + f"{items_name} x{count}")
                            else:
                                print(Fore.MAGENTA + Style.BRIGHT + f"{items_name} x{count * 2}")
                        else:
                            if quest.isIncreasedResult_ == 0:
                                print(Fore.MAGENTA + Style.BRIGHT + f"{items_name} x{count}")
                            else:
                                print(Fore.MAGENTA + Style.BRIGHT + f"{items_name} x{count * 3}")

                except Exception as e:
                    print(Fore.RED + Style.BRIGHT + 'An error occurred:', e)

    if 'user' not in decoded:
            print(Fore.RED + Style.BRIGHT +
                  "error when sending finishing to quest : " + str(r.json()))
            return
    else:
        if gems > 0 : 
            print(Fore.BLUE + Style.BRIGHT +"Gems: " +  str(gems))
        print(Fore.BLUE + Style.BRIGHT + "Berry: " + str(berry))
        print(Fore.GREEN + Style.BRIGHT + 'Completed stage ' + 'ID ' + str(stage_id))  
    return 

def complete_unfinished_quest_stages():
    # gestionnaire pour les modèles
    db.Model.set_connection_resolver(db.db_glb)

    # Récupération de tout le contenue de la table "MstQuest_"
    quests = db.quest.all()

    # Récupération de tous les enregistrements où la colonne "questId_" est similaire à "%%"
    quests = db.quest.where("questId_", "like", "%%").get()
    user_errands = user.user_errands()
    
    challenge_id = [20000001,20000002,20000003,20000004,20000005,20000006,20000007,
                    20000008,20000009,20000010,20000011,20000012,20000013,20000014,
                    20000015,20000016,20000017,20000018,20000019,20000020,20000021,
                    20000022,20000023,20000024,20000025,20000026,20000027,20000028]
    
    for id in quests:
        if id.questId_ not in user_errands:
            stage_id = id.questId_
            if stage_id <= 542:
                complete_stage(str(stage_id))
            else:
                for challenge in challenge_id:
                    if challenge not in user_errands:
                        complete_stage(str(challenge))
                print("#######################################")
                print("Story finished")
                return 0     
            
    autosell(unit=None)
    return 0
       
def complete_unfinished_event_stages():
    # gestionnaire pour les modèles
    db.Model.set_connection_resolver(db.db_glb)

    #date ici

    # Définir le fuseau horaire PST
    pst = pytz.timezone('America/Los_Angeles')

    # Obtenir la date et l'heure actuelles dans le fuseau horaire
    current_date = datetime.datetime.now(pst)

    # Obtenir le nom du jour de la semaine
    day_of_week = current_date.strftime('%A')

    # Dictionnaire de jours de la semaine en anglais
    weekday_dict = {
        "Sunday": 0,
        "Monday": 1,
        "Tuesday": 2,
        "Wednesday": 3,
        "Thursday": 4,
        "Friday": 5,
        "Saturday": 6
    }

    # Récupérer le numéro de jour de la semaine
    weekday_number = weekday_dict[day_of_week]
    date_string = current_date.strftime("%Y%m%d")
    
    event_shedule = db.events_schedule.where('eventId_', 'like', "%%").get()
    quests = db.quest.where("questId_", "like", "%%").get()
    
    dates = []
    event_ids = []
    
    ban = [7434,7435,7432,7433,7427,7428,550103,7421,7422,9502,9503,9504,9505,9506,9507,9508,9509,9510,9511,9512,9513,9514,9515,9516,9517,350362,350363,8001,8003,8004,9001,9002,9003,9004,13245407,13245403,13245411,13245423,13245427,13245439,13245443,13245447,13245461,13245465,13245469,13245477,13245281,13245387,13245515,13245505,13245485,13245511,9850351,9850352,13245237,13245241,13245253,13245261,13245265,13245269,13245277,13245289,13245293,13245301,13245313,13245317,13245329,13245337,13245353,13245357,13245361,13245375,13245379,13245383,9850353,9850354,9850355,9850356,9850357,9850358,13245273,13245305,13245285,13245325,13245341,13245391,13245431,13245435,13245457,13245513,6001,350043,310098,310099,310101,310102,3000558,7161,7176,6176,6185,6202,6367,6399,6772,6835,6884,7405,7406,310021,310022,310023,310024,310025,310026,310027,310028,310029,310030,310031,310032,310033,310034,310035,310036,310037,310038,310039,310040,310041,310042,310043,310044,310045,310046,310047,310048,310049,310050,310051,310086,310087,310088,310089,310090,310091,310092,310093,310094,310095,310096,310097,7001,7003]
    area_ban = [9000,8000,6000,6001,6002]
    
    user_errands = user.user_errands()
    
    for ban_kizuna_tm_area in quests:
        if ban_kizuna_tm_area.areaId_ in area_ban or ban_kizuna_tm_area.questName_ == "One time only special quest!" :
            ban.append(ban_kizuna_tm_area.questId_)
      
    for dateweek in event_shedule:
        dates = []
        dates.append(dateweek.dayOfWeek_)
        if dateweek.dayOfWeek_ == -1:
            if dateweek.finishDate_ >= int(date_string):
                correct_ids = []
                correct_ids.append(dateweek.eventId_)
                event_id = db.eventsRelation.where_in("eventId_", correct_ids).get()
                for final_id in event_id:
                    if final_id.questId_ not in event_ids:
                        event_ids.append(final_id.questId_)

            if dateweek.finishDate_ == -1:
                correct_ids = []
                correct_ids.append(dateweek.eventId_)
                event_id = db.eventsRelation.where_in("eventId_", correct_ids).get()
                for final_id in event_id:
                    if final_id.questId_ not in event_ids:
                        event_ids.append(final_id.questId_) 

        if weekday_number in dates:
            correct_ids = []
            correct_ids.append(dateweek.eventId_)
            event_id = db.eventsRelation.where_in("eventId_", correct_ids).get()
            for final_id in event_id:
                if final_id.questId_ not in event_ids:
                    event_ids.append(final_id.questId_) 
    
    for stage_id in event_ids:
        if stage_id not in ban and stage_id not in user_errands:
            complete_stage(str(stage_id))
    return
    
async def fetch_page(page):
    url = config.get_version() + '/user_characters.json?page=' + str(page)
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=config.session.headers)
        decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
        return json.loads(decoded.value.decode('utf-8'))

async def fetch_all_pages(total_page):
    tasks = [fetch_page(page) for page in range(1, total_page + 1)]
    return await asyncio.gather(*tasks)
    
def autosell(unit=None):
    
    url = config.get_version() + '/user_characters.json?page=1'
    r = config.session.get(url, headers=config.session.headers)
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))

    total_page = decoded['page_total']
    
    characters = []
    if unit == None:
        chars_sell = [63,64,65,66,67,68,69,70,71,72,73,74,75,76,133,134,142,143,144,182,
                    183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,
                    200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,
                    217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,
                    254,255,256,257,258,259,281,282,283,284,285,289,290,291,292,293,260,
                    261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,
                    278,279,299,300,301,342,343,344,345,346,347,348,349,362,363,364,365,
                    366,390,391,392,393,394,397,398,425,450,577,578,579,580,581,582,583,584,
                    585,586,715,716,717,784,754,718,719,912,1004,1005,1006,1007,1008,1009,
                    1010,1011,1012,1013,1014,1904,10624,11049,10623,11048,10382,11415,11416,
                    11417,11418,11419,10009,10010,10011,10012,10013,1911,1912,1913,1906,1907,
                    1908,1909,1910,1759,1840,1570,1716,1717,1718,1711,1397,1398,1399,1246,1087,
                    1247,659,890,451,1193,1194,1195,1196,1197,1198,766,767,768,769,770,771,772,
                    773,774,775,386,387,656,46,154,139,889,751,628,891,923,383,286,250,1715,660,
                    449,421,248,1233,234,158,626,624,453,1713,1250,1251,389,426,368,1975,10336,1729,1973,10458,10527,10410,1989,10305,10031,1819,10161,1983,10580,10839,10414,1950,1836,10152,1697,10096,10076,10190,10777,10150,1519,10840,10033,1207,982,10361,22,10288,10425,175,135,568,569,570,571,572,573,574,575,576,578,579,580,581,582,583,584,585,586,587,588,589,590,591,592,593,594,595,596,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,1397,1398,1399,1400,1401,1107,1108,1109,1110,1111,1480,1481,1479,1482,1483,1711,1712,1713,1714,1715,1716,1717,1718,1246,1247,1248,1249,1250,1251,10009,10010,10011,10012,10013,10053,10470,10471,10472,10473,10763,10762,10623,11048,10624,11049,10625,11050,133,134,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,177,178,63,64,65,66,67,68,69,70,71,72,73,74,75,76,224,225,226,227,228,229,230,231,232,233,254,255,256,257,258,289,290,291,292,293,281,282,283,284,285,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,299,300,301,363,366,365,362,364,391,394,393,390,392,385,386,387,388,389,567,568,569,570,571,572,573,574,575,577,578,579,580,581,582,583,584,585,586,587,588,589,590,591,592,593,594,595,596,661,662,663,766,767,768,769,770,771,772,773,774,775,715,716,717,718,719,755,756,757,758,759,909,910,911,912,913,898,888,889,890,1004,1005,1006,1007,1008,1009,1010,1011,1012,1013,1014,1193,1194,1195,1196,1197,1198,1035,1036,1037,1200,1202,1201,1199,1203,1246,1247,1248,1249,1250,1251,822,823,824,825,826,1397,1398,1399,1400,1401,1107,1108,1109,1110,1111,1480,1481,1479,1482,1483,1711,1712,1713,1714,1715,1716,1717,1718,1906,1907,1908,1909,1910,1911,1912,1913,10009,10010,10011,10012,10013,10541,10542,10543,10544,10545,10381,10382,10470,10471,10472,10473,10763,10762,10623,11048,10624,11049,10625,11050,11175,11176,11177,11178,11179,11415,11416,11417,11418,11419,25,296,21,280,287,288,340,341,500,501,502,625,627,629,750,753,752,925,1030,1031,1097,1474,1475,1476,1472,1477,1478,1514,1515,1606,1534,1568,1569,1608,1607,1675,1676,1677,1678,1609,1762,1763,1788,1789,1800,1801,1839,1841,1842,1944,1945,1946,1947,1948,1965,1966,1967,10050,10051,10052,10054,10063,10104,10105,10378,10377,10376,10475,10476,10477,10478,10479,10626,10645,10646,10647,10648,10764,10765,10766,11086,11087,11088,11089,11200,11201,11202,11203]
    else:
        chars_sell = [int(unit)]
    
    if unit != None:
        try:
            db.Model.set_connection_resolver(db.db_glb)
            card_info = db.characters.where("serverId_", str(unit)).first()
            print(Fore.YELLOW + Style.BRIGHT + f"Selected card id: {unit} name: {card_info.name_}")
        except:
            print(Fore.RED + Style.BRIGHT + 'An error occurred:')
            return 0
    
    for page in range(1, total_page+1):
        url = config.get_version() + '/user_characters.json?page=' + str(page)
        r = config.session.get(url, headers=config.session.headers)
        decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
        decoded = json.loads(decoded.value.decode('utf-8'))
        sys.stdout.write("Fetching user cards from servers... Page %d/%d\r" % (page, total_page))
        sys.stdout.flush()

        for user_character in decoded["user_characters"]:
            if user_character["character_id"] in chars_sell and (user_character["id"], user_character["quantity"]) not in characters:
                characters.append((user_character["id"], user_character["quantity"]))
    
    if unit == None:
        print(f"Useless cards from story mode (Bandits, ...) : {str(len(characters))}")
    
        
    if len(characters) == 0:
        print(Fore.RED + Style.BRIGHT + "No character to sell")
        return 0
    
    characters_by_pack = [characters[i:i+40] for i in range(0, len(characters), 40)]
    
    for pack in characters_by_pack:
        user_characters = [f'{{"id": {c[0]}, "quantity": {c[1]}}}' for c in pack]
        user_characters = ','.join(user_characters)
        
        data1 = "{" + f'"user_characters": [{user_characters}], "result": true' +"}"
        encoded_data = cryption.Encrypt(config.get_session_key(), data1)
        data2 = {'encoded': True,
                 'data': encoded_data.decode('utf-8')}

        url = config.get_version() + '/user_characters/sell/'
        r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)

        decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
        decoded = json.loads(decoded.value.decode('utf-8'))

        if 'gain_money' in decoded:
            print(Fore.GREEN + Style.BRIGHT + f"Sold {len(pack)} characters for : " + Style.RESET_ALL +  Style.BRIGHT + str(decoded['gain_money']) + " Berrys")
        else:
            print(Fore.RED + Style.BRIGHT + decoded)
            return 0

def unlock_colosseum(group_boss_id):
    
    open_stage = user.my_data()
    
    points = user.get_user_point()['points']
    
    for data in open_stage:
        if str(group_boss_id) in str(data):
            print(Fore.RED + Style.BRIGHT + "Colosseum already unlocked.")
            return 0

    if points == 0:
        print(Fore.RED + Style.BRIGHT + "You have 0 points to unlock colosseum")
        return 0
    
    db.Model.set_connection_resolver(db.db_glb)
    colosseum_id = db.colosseum_group_boss.where("uniqueId_", "like", str(group_boss_id)).get()

    for id in colosseum_id:
        if id.colosseumGroupId_ == 1:
            url = config.get_version() + '/event_opens/5/execute'
        elif id.colosseumGroupId_ == 2:
            url = config.get_version() + '/event_opens/6/execute'
        elif id.colosseumGroupId_ == 3:
            url = config.get_version() + '/event_opens/7/execute'
    
    quests = db.quest.where("colosseumGroupBossId_", "like", str(group_boss_id)).get()
    
    data1 = '{"event_id":null,"colosseum_group_boss_id":'+f'{group_boss_id}'+'}'
    encoded_data = cryption.Encrypt(config.get_session_key(), data1)
    data2 = {'encoded': True,
             'data': encoded_data.decode('utf-8')}
    
    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
    
    if 'error' not in r.json():
        decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
        decoded = json.loads(decoded.value.decode('utf-8'))
        ids = []
        try:
            for quest_id in quests:
                ids.append(quest_id.questId_)
            for quests_id in ids:
                complete_stage(str(quests_id))
        except KeyboardInterrupt:
            return 0
    else:
        print(Fore.RED + Style.BRIGHT + str(r.json()))
        return 0
        
def farm_arena_cpu():
    url = config.get_version() + '/pirates_cpus.json'
    r = config.session.get(url, headers=config.session.headers)
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))
    
    code = []

    for id_code in decoded['pirates_cpus']:
        # if id_code['locked'] == False and 
        if id_code['cleared'] == False:
            code.append(id_code['user_code'])

    if len(code) != 0:
        user.autoteam(str(155651),pui=True,pvp=True)
    else:
        print(Fore.GREEN + Style.BRIGHT + "PVP bot already cleared.")
        return 0
    
    for c in code:
        #start
        print('Begin stage: ID :',c)
        url = config.get_version() + '/pirates_arena_battles/start'
        data1 = '{"user_code":'f' "{c}",'+ '"activate_deck_position": 1' + '}'
        
        encoded_data = cryption.Encrypt(config.get_session_key(), data1)
        data2 = {'encoded': True,
                'data': encoded_data.decode('utf-8')}
        r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
        
        decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
        decoded = json.loads(decoded.value.decode('utf-8'))
        id_arena = decoded['user_pirates_arena_battle_id']

        #execute
        url = config.get_version() + '/pirates_arena_battles/execute'
        data1 = '{"user_pirates_arena_battle_id":'f'{id_arena}'+'}'
        encoded_data = cryption.Encrypt(config.get_session_key(), data1)
        data2 = {'encoded': True,
                'data': encoded_data.decode('utf-8')}
        r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
        decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
        decoded = json.loads(decoded.value.decode('utf-8'))
        
        #finish
        url = config.get_version() + '/pirates_arena_battles/finish'
        data1 = '{"user_pirates_arena_battle_id":'f'{id_arena}'',"result_type": 1,"ally_dead_character_ids": [],"enemy_dead_character_ids": [],"ally_characters": [],"enemy_characters": [],"ally_leader_character": {"character_id": -1,"health_buff": 0,"attack_buff": 0,"regeneration_buff": 0,"armor_buff": 0,"speed_buff": 0,"skill_accumulate_buff": 0,"knockback_buff": 0,"guard_buff": 0,"critical_buff": 0,"miss_buff": 0,"base_health": 0,"base_attack": 0,"base_regeneration": 0,"base_armor": 0,"base_speed": 0,"base_skill_interval": null},"enemy_leader_character": {"character_id": -1,"health_buff": 0,"attack_buff": 0,"regeneration_buff": 0,"armor_buff": 0,"speed_buff": 0,"skill_accumulate_buff": 0,"knockback_buff": 0,"guard_buff": 0,"critical_buff": 0,"miss_buff": 0,"base_health": 0,"base_attack": 0,"base_regeneration": 0,"base_armor": 0,"base_speed": 0,"base_skill_interval": null},"burst_gauge_json": {"ally_leader_battle_log": {"limit": 0,"critical_count": 0,"guard_count": 0,"knockback_count": 0,"knockout_ally_count": 0,"knockout_enemy_count": 0,"give_damage_count": 0,"receive_damage_count": 0,"give_healing_count": 0,"receive_healing_count": 0,"leader_skill_turn_count": 0,"give_damage_value": 0,"receive_damage_value": 0,"receive_healing_value_ally": 0,"receive_healing_value_enemy": 0,"give_normal_attack_count": 0,"give_heavy_attack_count": 0,"give_full_attack_count": 0,"healing_action_count": 0,"give_abnormal_state_count": 0,"receive_abnormal_state_count": 0,"active_skill_ally_count": 0,"active_skill_enemy_count": 0,"burst_activation_timings": []},"enemy_leader_battle_log": {"limit": 0,"critical_count": 0,"guard_count": 0,"knockback_count": 0,"knockout_ally_count": 0,"knockout_enemy_count": 0,"give_damage_count": 0,"receive_damage_count": 0,"give_healing_count": 0,"receive_healing_count": 0,"leader_skill_turn_count": 0,"give_damage_value": 0,"receive_damage_value": 0,"receive_healing_value_ally": 0,"receive_healing_value_enemy": 0,"give_normal_attack_count": 0,"give_heavy_attack_count": 0,"give_full_attack_count": 0,"healing_action_count": 0,"give_abnormal_state_count": 0,"receive_abnormal_state_count": 0,"active_skill_ally_count": 0,"active_skill_enemy_count": 0,"burst_activation_timings": []' + '}' + '}' + ',"skip": false}'
        encoded_data = cryption.Encrypt(config.get_session_key(), data1)
        data2 = {'encoded': True,
                'data': encoded_data.decode('utf-8')}
        r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
        decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
        decoded = json.loads(decoded.value.decode('utf-8'))
        print(Fore.GREEN + Style.BRIGHT + 'Completed stage ID: ' + c )
        
def farm_grand_voyage():
    # gestionnaire pour les modèles
    db.Model.set_connection_resolver(db.db_glb)
    quests = db.grand_voyage.where("questId_", "like", "%%").get()
    ids = []
   
    for quest_id in quests:
        if quest_id.level_ == 1:
            ids.append(quest_id.questId_)
            
    for stage in ids:
        complete_stage(str(stage),gv=True)

def multi_acc(num):
    processus = []
    for i in range(num):
        p1 = multiprocessing.Process(target=auth.sign_up(), args=(i,))
        p2 = multiprocessing.Process(target=save_data.create_file(m=True), args=(i, True))
        p3 = multiprocessing.Process(target=tutorial.tutorial_finish(), args=(i,))
        processus.extend([p1, p2, p3])
        
    for p in processus:
        p.start()
    for p in processus:
        p.join()
    
    print(f"Created {num} accounts")



