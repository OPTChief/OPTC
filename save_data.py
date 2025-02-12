import config, auth
import os
from colorama import init, Fore, Style
import string
import random
# Coloroma autoreset
init(autoreset=True)


def create_file(limit=2,m=False):
    if not os.path.exists('saves/'):
        os.makedirs('saves')
    if m:
        letters = string.ascii_lowercase + string.digits
        filename = ''.join(random.choice(letters) for i in range(8)) 
    else:
        filename = input(Style.BRIGHT + "Enter a name for the file : ")

    if not filename.strip():
        print("The file name cannot be empty or contain only spaces.")
        return create_file()

    if os.path.exists(os.path.join('saves', filename)):
        print("A file with this name already exists. Please choose another name.")
        return create_file()

    try:
        f = open(os.path.join('saves/' + filename), 'w')
        f.write('uuid: ' + str(config.uuid) + '\n')
        f.write('platform: ' + str(config.platform) + '\n')
        f.write('adid: ' + str(config.adid) + '\n')
        f.write('udid: ' + str(config.udid) + '\n')
        f.write('host: ' + str(config.version) + '\n')
        f.close()
        print('--------------------------------------------')
        print(Fore.CYAN + Style.BRIGHT + 'Written details to file: ' + filename)
        print(Fore.RED + Style.BRIGHT + 'If ' + filename +
              ' is deleted your account will be lost if you haven\'t linked it!')
        print('--------------------------------------------')
    except Exception as e:
        print(e)


def load_save_file(filename=None):
    if not filename:
        file_name = input("Enter save file name : ")
    else:
        file_name = filename
        
    file_path = "saves/" + file_name
    try:
        with open(file_path, 'r') as file:
            for i, line in enumerate(file):
                key, value = line.strip().split(':')
                if i == 0:
                    config.uuid = str(value.strip())
                elif i == 1:
                    config.platform = str(value.strip())
                elif i == 2:
                    config.adid = str(value.strip())
                elif i == 3:
                    config.udid = str(value.strip())
                elif i == 4:
                    config.version = str(value.strip())
        auth.login()
    except FileNotFoundError:
        print("File not found.")
        load_save_file()
        return
