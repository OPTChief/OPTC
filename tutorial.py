import config,auth
import cryption
import json
from colorama import init, Fore, Back, Style
import user
# Coloroma autoreset
init(autoreset=True)
"""
Class description.
"""

def tutorial_init():
    """
    Sends first informations to Bandai Namco servers to init account for tutorial
    """
    print(Fore.BLUE + Style.BRIGHT +
                "Tutorial progess : 1/4...")
    
    data1 = '{"fellows_last_update_time":0}'
    
    encoded_data = cryption.Encrypt(config.get_session_key(), data1)
    data2 = {"encoded": True,
             "data": encoded_data.decode('utf-8')}
    
    url = config.get_version() + '/users/mydata.json'
    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
    
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))

    # #download data
    # url = config.get_version() + '/resources/resource_list_path.json'
    # r = config.session.get(url,headers=config.session.headers)

    # decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    # decoded = json.loads(decoded.value.decode('utf-8'))


    # resource_list = None

    # if 'resource_list_uri' in decoded:
    #     tmp = decoded["resource_list_uri"]
    #     resource_list = tmp.split("/")[-1]
    # else:
    #     print(Fore.RED + Style.BRIGHT + decoded)
    #     return
    
    # data1 = '{' + f'"resource_list": "{resource_list}"' +'}'
    # encoded_data = cryption.Encrypt(config.get_session_key(), data1)
    # data2 = {'encoded': True,
    #          'data': encoded_data.decode('utf-8')}

    # url = config.get_version() + '/download_bonuses/start'
    # r = config.session.post(url, data=json.dumps(data2),headers=config.session.headers)
   
    # decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    # decoded = json.loads(decoded.value.decode('utf-8'))

    # url = config.get_version() + '/download_bonuses/finish'
    # r = config.session.post(url, data=json.dumps(data2),headers=config.session.headers)
    # decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    # decoded = json.loads(decoded.value.decode('utf-8'))

    url = config.get_version() + "/users/total_login_bonus"
    r = config.session.get(url, headers=config.session.headers)
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))
    
    print(Fore.BLUE + Style.BRIGHT +
            "Tutorial progess : 2/4...")
    return 0


def tutorial_part4():
    """
    Part4
    """
    print(Fore.BLUE + Style.BRIGHT +
            "Tutorial progess : 3/4...")
    
    # # Train luffy
    # luffy = user.get_user_character_id(1)
    # turtle = user.get_user_character_id(118)
    # data1 = '{' + f'"master_user_character_id": {luffy}, "slave_user_character_ids": [{turtle}]'  +'}'
    # encoded_data = cryption.Encrypt(config.get_session_key(), data1)
    # data2 = {'encoded': True,
    #          'data': encoded_data.decode('utf-8')}
    
    # url = config.get_version() + '/tutorial_compositions/execute.json'
    
    # r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
    
    # decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    # decoded = json.loads(decoded.value.decode('utf-8'))
    # if 'current_user' not in decoded:
    #     print(Fore.RED + Style.BRIGHT +
    #               "error when sending progess to servers : " + r.json())
    #     return
    
    # # evolution luffy
    # turtle = user.get_user_character_id(82)
    # data1 = '{' + f'"master_user_character_id": {luffy}, "slave_user_character_ids": [{turtle}], "evolution_recipe_id": {1}'  +'}'
    
    # encoded_data = cryption.Encrypt(config.get_session_key(), data1)
    # data2 = {'encoded': True,
    #          'data': encoded_data.decode('utf-8')}
    # url = config.get_version() + '/tutorial_compositions/evolution_execute.json'
    
    # r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
    
    # decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    # decoded = json.loads(decoded.value.decode('utf-8'))
    # if 'current_user' not in decoded:
    #     print(Fore.RED + Style.BRIGHT +
    #               "error when sending progess to servers : " + r.json())
    #     return

    # This request is sent juste before /tutorials/finish
    data1 = {
      "sequence": 1,
      "don": 50,
      "point": 5
    }
    data1 = '{"sequence": 1,"don": 50,"point": 5}'
    encoded_data = cryption.Encrypt(config.get_session_key(), data1)
    data2 = {'encoded': True,
             'data': encoded_data.decode('utf-8')}
    
    url = config.get_version() + '/loading_game/add'
    
    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))


    # Finish tutorial
    data1 = '{ "_dummy": "1" }'
    encoded_data = cryption.Encrypt(config.get_session_key(), data1)
    data2 = {'encoded': True,
             'data': encoded_data.decode('utf-8')}
    
    url = config.get_version() + '/tutorials/finish'
    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))

    if 'status' in decoded:
        if decoded['status'] != 'ok':
            print(Fore.RED + Style.BRIGHT +
                  "error when sending finishing tutorial : " + r.json())
            return

    # Finish tutorial
    data1 = '{ "_dummy": "1" }'
    encoded_data = cryption.Encrypt(config.get_session_key(), data1)
    data2 = {'encoded': True,
             'data': encoded_data.decode('utf-8')}

    url = config.get_version() + '/user_login_stamp_campaigns/execute'
    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
    
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))


    if 'current_user' in decoded:
        pass
    else:
        print(Fore.RED + Style.BRIGHT + decoded)
        return
    
    data1 = '{' + f'"fellows_last_update_time": {915177600}' +'}'
    encoded_data = cryption.Encrypt(config.get_session_key(), data1)
    data2 = {'encoded': True,
             'data': encoded_data.decode('utf-8') }
    
    url = config.get_version() + '/users/mydata.json'
    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))

    if 'current_user' in decoded:
        pass
    else:
        print(Fore.RED + Style.BRIGHT + decoded)
        return
    
    url = config.get_version() + '/user_gacha_appearance_conditions'
    r = config.session.get(url, headers=config.session.headers)
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))
   
    # url = config.get_version() + '/app_informations.json?page=1'
    # r = config.session.get(url, headers=config.session.headers)
    # decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    # decoded = json.loads(decoded.value.decode('utf-8'))

    # 15th 
    data1 = '{"progress":1000}'
    
    encoded_data = cryption.Encrypt(config.get_session_key(), data1)
    data2 = {'encoded': True,
             'data': encoded_data.decode('utf-8')}
    
    url = config.get_version() + '/tutorials/log'
    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
    
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))

    if 'status' not in decoded:
        print(Fore.RED + Style.BRIGHT +
                  "error when sending progess to servers : " + decoded)
        return
        
    print(Fore.BLUE + Style.BRIGHT +
                  "Tutorial progess : 4/4...")
    return 0
    
def tutorial_finish():
    tutorial_init()
    tutorial_part4()
    print(Fore.BLUE + Style.BRIGHT + "Tutorial complete !")
    print("--------------------------------------------")
    auth.login()
