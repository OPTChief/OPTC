"""
Class to handle recruit
"""
import db
from colorama import init, Fore, Back, Style
import datetime
import webhook
import json
import config
from PIL import Image, ImageDraw
import requests
import io
import cryption

def generate_banner(images):
    num_images = len(images)
    num_rows = (num_images + 4) // 5  # Round up to nearest multiple of 5
    banner_width = 560  # 5 images per row, each 112 pixels wide
    banner_height = num_rows * 112
    
    banner = Image.new('RGBA', (banner_width, banner_height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(banner)
    
    for i, img_url in enumerate(images):
        char_id = img_url.split('/')[-1].split('_')[1].split('.')[0].zfill(4)  # Extract and pad character ID
        img_url_padded = img_url.replace(f"character_{char_id}", f"character_{char_id.zfill(4)}")  # Add padded character ID to URL
        
        try:
            img_data = requests.get(img_url_padded).content  # Get image data from URL
            img = Image.open(io.BytesIO(img_data)).convert('RGBA')  # Convert image to RGBA mode
            banner.paste(img, (i % 5 * 112, i // 5 * 112))  # Paste image onto banner at correct position
        except Exception as e:
            print(f"Error processing image at URL {img_url_padded}: {e}")
    # banner = generate_banner(images)
    # banner.show()  # Display the generated banner image
    # banner.save('banner.png')  # Save the generated banner image to file
    return banner

    

def get_payment_gachas():
    gacha_lst = []
    try:
        db.Model.set_connection_resolver(db.db_glb)
        current_timestamp = datetime.datetime.now().timestamp()
        gashas = db.gashas.where('startAt_', '<=', current_timestamp).where('endAt_', '>=', current_timestamp).where('gashaType_', '=', 'Gacha::Payment').get()
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + 'An error occurred:', e)
        return 0
    
    for gacha in gashas:
        end_date = datetime.datetime.fromtimestamp(gacha.endAt_)
        if end_date.year > 2024:
            continue
        json_value = json.loads(gacha.drawContents_)
        if not json_value:
            continue
        name = json_value[0]['title']

        # Check if gasha is free
        is_free = False
        freeUID = None
        free_gasha = db.gashas_free_schedule.where('gashaId_', '=', gacha.uniqueId_).first()
        if free_gasha:
            is_free = True
            freeUID = free_gasha.uniqueId_

        dict = {
            'ID': gacha.uniqueId_,
            'Name': name,
            'StartAt': gacha.startAt_,
            'EndAt': gacha.endAt_,
            'isFree': is_free,
            'freeUID': freeUID
        }
        gacha_lst.append(dict)
        
    sorted_gacha_lst = sorted(gacha_lst, key=lambda x: (not x['isFree']), reverse=True)
    return sorted_gacha_lst

def recruit():
    
    gacha_lst = get_payment_gachas()
    display_gacha = []
    for i, dic in enumerate(gacha_lst):
        if dic['isFree'] :
            display_gacha.append(f"{Fore.BLUE + Style.BRIGHT}{i}  {Style.RESET_ALL}|{Fore.LIGHTGREEN_EX + Style.BRIGHT} [FREE] {dic['Name']} {Style.RESET_ALL}| ID : {dic['ID']}")
        else:
            display_gacha.append(f"{Fore.BLUE + Style.BRIGHT}{i}  {Style.RESET_ALL}|{Fore.YELLOW + Style.BRIGHT} {dic['Name']} {Style.RESET_ALL}| ID : {dic['ID']}")
    
    while True:
        for elem in display_gacha:
            print(elem)
        try:
            id = int(input(Style.BRIGHT + "\nHold ctrl + c to go back to menu\nOn which banner would you like to recruit (option 0, 1, 2,...): ").strip())
            type = int(input(Style.BRIGHT + "Choose between 1 or 2:\nMulti : 1\nSingle: 2\nYour choice : ").strip())
            if id == -1:
                break
            if (-1 < id < len(display_gacha)) == False or (type != 1 and type != 2):
                print(f"{Fore.RED + Style.BRIGHT}Please select a valid option.")
                continue
            if type == 1:
                counter = int(input(Style.BRIGHT + "How many Multi(s) ? : ").strip())
                total = 10
            else:
                counter = int(input(Style.BRIGHT + "How many Single(s) ? : ").strip())
                total = 1
                
            
            while counter:
                if gacha_lst[id]['isFree']:
                    
                    url = config.get_version() + f"/limited_free_gachas/remain_count"
                    
                    r = config.session.get(url, headers=config.session.headers)
                    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
                    decoded = json.loads(decoded.value.decode('utf-8'))
                    data = json.loads(decoded['limited_free_gachas'])
                    
                    available = True
                    for item in data:
                        if item['gacha_free_schedule_id'] == gacha_lst[id]["freeUID"] and item['remain_draw_count'] == 0:
                            print(Fore.RED + Style.BRIGHT +"\nThe Free Rare Recruit this banner period has been used.\n")
                            counter = -1
                            available = False
                            break
                                                
                    if available == False: break
                    
                    url = config.get_version() + f"/limited_free_gachas/{gacha_lst[id]['ID']}/confirm.json?probability_start_at={gacha_lst[id]['StartAt']}"
                    data1 = "{"+f'"id":{gacha_lst[id]["ID"]},"gacha_free_schedule_id":{gacha_lst[id]["freeUID"]}'+"}"
                    
                    encoded_data = cryption.Encrypt(config.get_session_key(), data1)
                    data2 = {'encoded': True,
                                'data': encoded_data.decode('utf-8')}
                    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
                    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
                    decoded = json.loads(decoded.value.decode('utf-8'))
                    transaction_id = decoded['transaction_id']
                    
                    url = config.get_version() + f"/limited_free_gachas/{gacha_lst[id]['ID']}/execute.json?probability_start_at={gacha_lst[id]['StartAt']}"                                                                                
                    data1 = "{"+f'"gacha_free_schedule_id":{gacha_lst[id]["freeUID"]},"transaction_id":{transaction_id}'+"}"
                    encoded_data = cryption.Encrypt(config.get_session_key(), data1)
                    data2 = {'encoded': True,
                            'data': encoded_data.decode('utf-8')}
                    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
                    
                    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
                    decoded = json.loads(decoded.value.decode('utf-8'))
                    
                else:
                    url = config.get_version() + f"/payment_gachas/{gacha_lst[id]['ID']}/confirm.json?probability_start_at={gacha_lst[id]['StartAt']}"
                    data1 = "{"+f'"id":{gacha_lst[id]["ID"]},"total":{total}'+"}"
                
                    encoded_data = cryption.Encrypt(config.get_session_key(), data1)
                    data2 = {'encoded': True,
                                'data': encoded_data.decode('utf-8')}
                    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
                    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
                    decoded = json.loads(decoded.value.decode('utf-8'))
                    transaction_id = decoded['transaction_id']
                    
                    url = config.get_version() + f"/payment_gachas/{gacha_lst[id]['ID']}/execute.json?probability_start_at={gacha_lst[id]['StartAt']}"                                                                                
                    data1 = "{"+f'"total":{total},"transaction_id":{transaction_id},"transaction_type":{1}'+"}"
                    encoded_data = cryption.Encrypt(config.get_session_key(), data1)
                    data2 = {'encoded': True,
                            'data': encoded_data.decode('utf-8')}
                    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
                    
                    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
                    decoded = json.loads(decoded.value.decode('utf-8'))
                
                remaining_gems = decoded['current_user']['dpoint']
                drop = []
                images = []
                data_dict = {}
                
                for character in decoded['user_characters']:
                    drop.append(character['character_id'])
                    character_id_padded = str(character['character_id']).zfill(4)
                    images.append(f"https://cdn.gb.onepiece-tc.jp/en/images/characters/character_{character_id_padded}_t.png")

                    
                db.Model.set_connection_resolver(db.db_glb)
                db_card = db.characters.where_in("serverId_", drop).get()
                
                drop.clear()
                
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
                    drop.append(data_dict)
                # create a list to store the output
                output_list = []
                for i, value in enumerate(drop):
                    if int(value['Rarity']) == 5:
                        output_list.append(Fore.YELLOW + Style.BRIGHT + value['Name'] + " (" + value['SubName'] + ") " + value['Type1']+ " | " + "Rarity : "+ value['Rarity']+"★")
                    elif int(value['Rarity']) >5:
                        output_list.append(Back.LIGHTRED_EX + Fore.WHITE + Style.BRIGHT + value['Name'] + " (" + value['SubName'] + ") " + value['Type1']+ " | " + "Rarity : "+ value['Rarity']+"★")
                    else:
                        output_list.append(value['Name'] + " (" + value['SubName'] + ") " + value['Type1']+ " | " + "Rarity : "+ value['Rarity']+"★")
                output_list.append(Fore.MAGENTA + Style.BRIGHT + 'Gems remaining: ' + str(remaining_gems))
                print(Fore.WHITE + Style.BRIGHT +"\n##########################################")
                for e in output_list:
                    print(e)
                print(Fore.WHITE + Style.BRIGHT +"##########################################\n")
                
                if config.premium and config.toggle_summon:
                    banner = generate_banner(images)
                    banner.show()
                    banner.save('summon.png') 
                    # Save the generated banner image to file
                    # webhook.post_webhook_with_image(
                    #     config.imgur_client_id,
                    #     config.imgur_client_secret,
                    #     "summon.png",
                    #     f"{config.username} summons result",
                    #     config.webhook_url,
                    #     gacha_lst[id]['Name']
                    # )
                counter -= 1
            
        except Exception as e:
            print(e)
            return
                    
    return   
