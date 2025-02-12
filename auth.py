import config,user
import utils
import cryption
import json
from colorama import init, Fore, Style
import sys
# Coloroma autoreset
init(autoreset=True)
"""
Class description.
"""

def sign_up():

    url = config.get_version() + '/users/register'

    dec_data = None
    config.uuid = utils.generate_uuid()  # Identifier
    config.adid = utils.generate_gaid()  # Android
    config.udid = utils.generate_idfa()  # iOS

    if config.version == 'gb':
        if config.platform == 'android':
            dec_data = '{'+f'"uuid":"{config.uuid}","adid":"{config.adid}","country_code":"CA","currency_unit":"CAD","idfa":"00000000-0000-0000-0000-000000000000","locale":"en"'

        elif config.platform == 'ios':
            dec_data = '{'+f'"uuid":"{config.uuid}","udid":"{config.udid}","country_code":"CA","currency_unit":"CAD","idfa":"00000000-0000-0000-0000-000000000000","locale":"en"'

    elif config.version == 'jp':
        if config.platform == 'android':
            dec_data = '{'+f'"uuid":"{config.uuid}","adid":"{config.adid}","country_code":"CA","currency_unit":"CAD","idfa":"00000000-0000-0000-0000-000000000000"'

        elif config.platform == 'ios':
            dec_data = '{'+f'"uuid":"{config.uuid}","udid":"{config.udid}","country_code":"CA","currency_unit":"CAD","idfa":"00000000-0000-0000-0000-000000000000"'
    else:
        print("error when signing up")
        sys.exit(0)

    # Set init session key
    k = cryption.CreateFromKey("vuyWQSjlknpJF54ib36txVse")
    config.init_session_key = k

    encoded_data = cryption.Encrypt(config.init_session_key, dec_data)
    data1 = {'encoded': True,
             'data': encoded_data.decode('utf-8')}
    config.init_session_1()
    r = config.session.post(url, data=json.dumps(data1), headers=config.session.headers)

    decoded = cryption.Decrypt(config.init_session_key, r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))
    config.bq159_key = decoded["bq159_key"]
    config.session_key = cryption.CreateFromKey(config.bq159_key)
    config.sakura_session = decoded["session_id"]
    config.init_session_2()
    print(Fore.GREEN + Style.BRIGHT + 'Account created successfully.')
    print("--------------------------------------------")

    
def login():

    url = config.get_version() + '/users/sessions'

    dec_data = None
    if config.version == 'gb':
        if config.platform == 'android':
            dec_data = '{'+f'"uuid":"{config.uuid}","adid":"{config.adid}","country_code":"CA","currency_unit":"CAD","idfa":"00000000-0000-0000-0000-000000000000"'

        elif config.platform == 'ios':
            dec_data = '{'+f'"uuid":"{config.uuid}","udid":"{config.udid}","country_code":"CA","currency_unit":"CAD","idfa":"00000000-0000-0000-0000-000000000000"'

    elif config.version == 'jp':
        if config.platform == 'android':
            dec_data = '{'+f'"uuid":"{config.uuid}","adid":"{config.adid}","country_code":"CA","currency_unit":"CAD","idfa":"00000000-0000-0000-0000-000000000000"'

        elif config.platform == 'ios':
            dec_data = '{'+f'"uuid":"{config.uuid}","udid":"{config.udid}","country_code":"CA","currency_unit":"CAD","idfa":"00000000-0000-0000-0000-000000000000"'

    # Set init session key
    k = cryption.CreateFromKey("vuyWQSjlknpJF54ib36txVse")
    config.init_session_key = k

    encoded_data = cryption.Encrypt(config.init_session_key, dec_data)
    data1 = {'encoded': True,
             'data': encoded_data.decode('utf-8')}
    r = config.session.post(url, data=json.dumps(data1), headers=config.session.headers)

    decoded = cryption.Decrypt(config.init_session_key, r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))
    try:
        config.bq159_key = decoded["bq159_key"]
        config.session_key = cryption.CreateFromKey(config.bq159_key)
        config.sakura_session = decoded["session_id"]
        config.init_session_2()
        print(Fore.BLUE + Style.BRIGHT + 'Retreiving user infos...' + Style.RESET_ALL)
        user.user_login_bonuses()
        user.user_login_stamp()
        print(Fore.BLUE + Style.BRIGHT + 'SIGN IN COMPLETE' + Style.RESET_ALL)
        print("--------------------------------------------")
    except KeyError:
        print(Fore.RED + Style.BRIGHT + decoded)
        sys.exit(0)
    

