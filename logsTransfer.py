import config, auth
import cryption
import json
import transferConsts
from colorama import init, Fore, Style
import save_data
# Coloroma autoreset
init(autoreset=True)


"""
Class which contains functions to send to users their ID and Password if they want to change device or transfer data.
"""


def generate_ID_and_password():
    """
    Generates ID and Password for data transfer
    """
    url = config.get_version() + '/accounts'

    r = config.session.get(url, headers=config.session.headers)

    key = config.session_key

    decoded = cryption.Decrypt(key, r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))
    user_code = decoded['user_code']
    passcode = decoded['passcode']
    
    if decoded['exist_account'] == False:
        exist_account = False
    else:
        exist_account = True

    # Headers and URL still the same if account doesnt exist
    if exist_account == True:
        url = config.get_version() + '/accounts/update'
    
    data1 = '{"account":{'+f'"password":"{passcode}","password_confirmation":"{passcode}","user_code":"{user_code}"'+'}'+'}'
    
    encoded_data = cryption.Encrypt(key, data1)
    
    data2 = {'encoded': True,
             'data': encoded_data.decode('utf-8')}
    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
    decoded = cryption.Decrypt(key, r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))
    expiration_date = decoded['password_expire']

    # Stores data
    transferConsts.user_code, transferConsts.passcode, transferConsts.expiration_date = user_code, passcode, expiration_date

    print(Style.BRIGHT + 'Info : ')
    print(Fore.BLUE + Style.BRIGHT + 'User ID : ' + Style.RESET_ALL + user_code)
    print(Fore.BLUE + Style.BRIGHT + 'Password : ' + Style.RESET_ALL + passcode)
    print(Fore.BLUE + Style.BRIGHT + 'Expiration date : ' +
          Style.RESET_ALL + expiration_date)
    print("--------------------------------------------")

#link your account to the bot with id/password 
def login_transfer_code():
    
    url = config.get_version() + '/accounts/sign_in'

    id = input("Enter your transfer id: ")
    password = input("Enter your transfer code: ")

    data1 = '{' + '"account":{"password":' + f'"{password}","password_confirmation":"{password}","user_code":"{id}"' + '}' + '}'

    encoded_data = cryption.Encrypt(config.get_session_key(), data1)
    data2 = {'encoded': True,
             'data': encoded_data.decode('utf-8')}

    r = config.session.post(url, data=json.dumps(data2), headers=config.session.headers)
   
    if "error" in r.json():
        print(Fore.RED + Style.BRIGHT + str(r.json()))   
        return login_transfer_code()
    else:
        print(Fore.GREEN + Style.BRIGHT + 'Migration completed.')
        save_data.create_file()
        
    auth.login()
