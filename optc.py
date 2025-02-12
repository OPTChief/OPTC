from datetime import datetime, timedelta
import webbrowser
from colorama import init, Fore, Style
import requests
from orator import Schema
import sys
import config, auth,tutorial,database
import logsTransfer
import save_data,user_cmd, user,farm
import os
import subprocess
from tqdm import tqdm
init(autoreset=True)

# before anything a request for new URL & API port is required.
def checkGameVer():
    headers = {
        'Host': config.get_host(),
        'Content-type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': config.get_user_agent(),
        'Authorization': 'Basic c2FrdXJhOjBubHkwbmU=',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'close'
    }
    url = "https://app.gb.onepiece-tc.jp/client_requirements/need_update?locale=en"
    r = requests.get(url, headers=headers)
    if r.json()['now_version'] != config.now_version:
        config.now_version = r.json()['now_version'] 
    else:
        return 0
    
def download_file_from_github(url, destination_path):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    block_size = 8192  # Adjust the block size as per your preference
    progress_bar = tqdm(total=total_size, unit="B", unit_scale=True)
    with open(destination_path, "wb") as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()

def checkBotUpdate():
    url = "https://raw.githubusercontent.com/daye10/smile/master/optc-info.json"
    r = requests.get(url)
    info = r.json()
    if info["bot_version"] != config.bot_version:
        print(Fore.YELLOW + "Bot Update: A newer version of the bot is required. Updating...")
        # update_url = "https://github.com/daye10/smile/raw/master/smile.exe"
        # destination_path = f"smile_v{info['bot_version']}.exe"  
        # download_file_from_github(update_url, destination_path)
        # subprocess.run(destination_path) 
        sys.exit()
    else:
        return 0
       
def start():
    
    checkGameVer()
    checkBotUpdate()

    print('\n')
    print(f"{Fore.CYAN + Style.BRIGHT}Choose a version & plateform")
    print(f"{'-'*33}\n")
    while True:
        client = input(f"Which version ? ({Fore.YELLOW + Style.BRIGHT}Jp: 1{Style.RESET_ALL} or {Fore.YELLOW + Style.BRIGHT}Global: 2{Style.RESET_ALL}): ")
        if client.lower() == '1':
            config.version ='jp'
            break
        elif client.lower() == '2':
            config.version = 'gb'
            break
        else:
            continue

    while True:
        client = input(f"Which platform ? ({Fore.YELLOW + Style.BRIGHT}ios: 1{Style.RESET_ALL} or {Fore.YELLOW + Style.BRIGHT}android: 2{Style.RESET_ALL}): ")
        if client.lower() == '1':
            config.platform ='ios'
            break
        elif client.lower() == '2':
            config.platform = 'android'
            break
        else:
            continue
        
    command = ''
    config.init_session_1()
    while command != 'exit':
        # User Options
        print(' ')
        if command == '':
            while True:
                    print('---------------------------------')
                    print(Fore.CYAN  + Style.BRIGHT + 'New Account :' + Fore.YELLOW + Style.BRIGHT + ' 0') 
                    print(Fore.CYAN  + Style.BRIGHT + 'Log in with transfer code :' + Fore.YELLOW + Style.BRIGHT + ' 1') 
                    print(Fore.CYAN + Style.BRIGHT + 'Log in with save :' + Fore.YELLOW + Style.BRIGHT + ' 2')
                    print(Fore.CYAN + Style.BRIGHT + 'Perform daily login and daily events on each save :' + Fore.YELLOW + Style.BRIGHT + ' 3')
                    print('---------------------------------')
                    
                    command = input('Enter your choice: ')
                    if command == '0':
                        auth.sign_up()
                        save_data.create_file()
                        database.check_database()
                        tutorial.tutorial_finish()
                        print(' ')
                        break
                    elif command == '1':
                        input(Fore.YELLOW  + Style.BRIGHT + f"WARNING : Make sure that you're not changing platform (current plaform : {config.platform})\nHit Enter to continue... ")
                        auth.sign_up()
                        logsTransfer.login_transfer_code()
                        database.check_database()
                        print(' ')
                        break
                    elif command == '2':
                        save_data.load_save_file()
                        database.check_database()
                        print(' ')
                        break
                    elif command == '3':
                        files = os.listdir('saves')
                        for filename in files:
                            print(f"save : {filename}")
                            save_data.load_save_file(filename)
                            database.check_database()
                            user.accept_gifts()
                            user.user_info()
                            print(Style.BRIGHT + '---------------------------------')
                    else:
                        print(Fore.RED + Style.BRIGHT + "Command not understood")

            while True:
                print('---------------------------------')
                print(Fore.CYAN + Style.BRIGHT + "Type" + Fore.YELLOW + Style.BRIGHT + "'help'" + Fore.CYAN + Style.BRIGHT + " to view all commands.")
                try:
                    command_line = input()
                except:
                    sys.stdin = sys.__stdin__
                    command_line = input()

                if command_line == 'exit':
                    command = ''  
                    break  

                
                parts = command_line.split()
                command = parts[0]
                #stage
                stage = None
                times = None
                #team
                type_color = None
                #autosell
                unit = None
                if command == 'stage':
                    if len(parts) == 3:
                        stage = parts[1]
                        times = parts[2]
                    else:
                        print(Fore.RED + Style.BRIGHT + 'Usage: stage stage_id times')
                        continue  
                elif command == 'autoteam':
                    if len(parts) == 2:
                        type_color = parts[1]
                    else:
                        print(Fore.RED + Style.BRIGHT + 'Usage: autoteam str')
                        continue 
                elif command == 'autosell':
                    if len(parts) == 2:
                        unit = parts[1]
                    else:
                        farm.autosell(unit=None)
                        continue
                try:
                    user_cmd.user_command_executor(command, stage, times, type_color, unit)
                except KeyboardInterrupt:
                    print(Fore.CYAN + Style.BRIGHT + 'User interrupted process.')
                except Exception as e:
                    print(Fore.RED + Style.BRIGHT + repr(e))
