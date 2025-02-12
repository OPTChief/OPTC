from colorama import init, Fore, Style
import datetime
import pytz
import db
import quests as questGUI
# Coloroma autoreset
init(autoreset=True)

def available_quests():

    quests_lst = []
    print("Fetching quests from database...")
    try:
        db.Model.set_connection_resolver(db.db_glb)
        quests = db.quest.where('questId_', '<=', 542).get()
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + 'An error occurred:', e)
        return 0
    
    for quest in quests:

        dict = {
            'Description': quest.questName_,
            'ID': quest.questId_,
            'Area' : quest.areaId_
        }
        quests_lst.append(dict)
    
    # Sort quests
    print(Fore.CYAN + Style.BRIGHT + "Sorting quests...")
    quests_lst = sorted(quests_lst, key=lambda k: k['Area'])
    quests_lst = sorted(quests_lst, key=lambda k: k['ID'])
    print(Fore.GREEN + Style.BRIGHT + "Done !")
    
    display_quests = []
    for quest in quests_lst:
        display_quests.append(
            str(quest['Area']) + ' | ' + quest['Description'] + ' | ' + str(quest['ID']))
        
    t = questGUI.QuestListGUI(display_quests)
    t.display()
    return 0

def available_events():

    quests_lst = []
    print("Fetching events from database...")
    try:
        db.Model.set_connection_resolver(db.db_glb)
        quests = db.quest.where_in('questId_', get_events()).get()
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + 'An error occurred:', e)
        return 0
    
    for quest in quests:
        dict = {
            'Description': quest.questName_,
            'ID': quest.questId_,
            'Area' : quest.areaId_
        }
        quests_lst.append(dict)
    
    # Sort quests
    print(Fore.CYAN + Style.BRIGHT + "Sorting events...")
    quests_lst = sorted(quests_lst, key=lambda k: k['Area'])
    quests_lst = sorted(quests_lst, key=lambda k: k['ID'])
    print(Fore.GREEN + Style.BRIGHT + "Done !")
    
    display_quests = []
    for quest in quests_lst:
        display_quests.append(
            str(quest['Area']) + ' | ' + quest['Description'] + ' | ' + str(quest['ID']))
        
    t = questGUI.QuestListGUI(display_quests)
    t.display()
    return 0


def get_events():
    # gestionnaire pour les modèles
    db.Model.set_connection_resolver(db.db_glb)

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
    result = []
    ban = [7434,7435,7432,7433,7427,7428,7421,7422,9502,9503,9504,9505,9506,9507,9508,9509,9510,9511,9512,9513,9514,9515,9516,9517,350362,350363,8001,8003,8004,9001,9002,9003,9004,13245407,13245403,13245411,13245423,13245427,13245439,13245443,13245447,13245461,13245465,13245469,13245477,13245281,13245387,13245515,13245505,13245485,13245511,9850351,9850352,13245237,13245241,13245253,13245261,13245265,13245269,13245277,13245289,13245293,13245301,13245313,13245317,13245329,13245337,13245353,13245357,13245361,13245375,13245379,13245383,9850353,9850354,9850355,9850356,9850357,9850358,13245273,13245305,13245285,13245325,13245341,13245391,13245431,13245435,13245457,13245513,6001,350043,310098,310099,310101,310102,3000558,7161,7176,6176,6185,6202,6367,6399,6772,6835,6884,7405,7406,310021,310022,310023,310024,310025,310026,310027,310028,310029,310030,310031,310032,310033,310034,310035,310036,310037,310038,310039,310040,310041,310042,310043,310044,310045,310046,310047,310048,310049,310050,310051,310086,310087,310088,310089,310090,310091,310092,310093,310094,310095,310096,310097,7001,7003]
    area_ban = [9000,8000,6000,6001,6002]
    
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
        if stage_id not in ban:
            result.append(stage_id)
        
    return result
def get_colosseum():
    collo_group = {
        1: "-------------------------------------------------------- CHAOS: 100 POINTS REQUIRED--------------------------------------------------------",
        2: "-------------------------------------------------------- UNDERGROUND: 50 POINTS REQUIRED --------------------------------------------------------",
        3: "-------------------------------------------------------- EXHIBITION: 20 POINTS REQUIRED --------------------------------------------------------",
    }
    
    db.Model.set_connection_resolver(db.db_glb)

    result = []
    for colo in collo_group:
        coloseum = db.colosseum_group_boss.where("colosseumGroupId_", "like", str(colo)).get()
        result.append(collo_group[colo])
        for group in coloseum:
            if group.eventOpenEnabled_ == 1:
                result.append((str(group.uniqueId_), group.title_))

    questGUI.show2(result)


