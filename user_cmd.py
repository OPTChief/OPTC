import os
import sys
import io
import user,events
import logsTransfer
import farm
import consts
from colorama import *
import utils
import webbrowser
import config
import summon
init(autoreset=True)



def user_command_executor(command, stage=None, times=None, type_color=None, unit=None):
    if command == 'help':
        if getattr(sys, 'frozen', False):
            help_file_path = os.path.join(sys._MEIPASS, 'help.txt')
        else:
            help_file_path = 'help.txt'
        if os.path.exists(help_file_path):
            with open(help_file_path, 'r') as f:
                help_text = f.read()
                print(help_text)
        else:
            print(Fore.RED + Style.BRIGHT + 'help.txt does not exist.')
    
    elif command == 'discord':
        webbrowser.open("https://discord.gg/q59QbpqH2Z")
    elif command == 'info':
        user.user_info()
    elif command == 'exit':
        return
    elif command == 'quests':
        farm.complete_unfinished_quest_stages()
    elif command == 'events':
        farm.complete_unfinished_event_stages()
    elif command == 'pvp':
        farm.farm_arena_cpu()
    elif command == 'omegafarm':
        farm.complete_unfinished_quest_stages()
        farm.complete_unfinished_event_stages()
        farm.autosell()
        if config.premium:
            farm.farm_grand_voyage()      
    elif command == 'grandvoyage':
        if config.premium:
            farm.farm_grand_voyage()
        else:
            print(Fore.RED + Style.BRIGHT + 'You need to be patreon to use this command.') 
    elif command == 'rank':
        user.get_rank()
    elif command == 'recruit':
        summon.recruit()
    elif command == 'gift':
        user.accept_gifts()
    elif command == 'team':
        if config.premium:
            user.change_ship()
        user.change_team()
    elif command == 'transfer':
        logsTransfer.generate_ID_and_password()
    elif command == 'listquests':
        events.available_quests()
    elif command == 'listevents':
        events.available_events()
    elif command == 'autosell':
        if unit == None:
            print(Fore.RED + Style.BRIGHT + 'Usage: autosell id')
            return
        if unit.isdigit():
            farm.autosell(unit)
        else:
            print(Fore.RED + Style.BRIGHT + 'Usage: autosell id')
    elif command == 'invitation':
        user.invitations()
    elif command == 'nickname':
        user.change_nickname()
    elif command == 'tsummon':
        config.toggle_summon = not config.toggle_summon
        print(f"Toggle image state: {config.toggle_summon}")
    elif command == 'tmeat':
        config.toggle_meat = not config.toggle_meat
        print(f"Toggle meat state: {config.toggle_meat}")
    elif command == 'friend':
        if config.premium:
            config.friend_id = utils.suggest_character()
        else:
            print('Patreons can choose friend leader.\nBase friend leader : Chopper.')
            
        print(f"Run stages with a friend leader state : {[config.select_friend]} ")
    
    elif command == 'friendoff':
        config.select_friend = False
        print(f"Run stages with a friend leader state [OFF]")

    elif command == 'frequest':
        if config.premium:
            f_id = input("Enter the friend id: ")
            user.send_friend_requests(f_id)
        else:
            print(Fore.RED + Style.BRIGHT + 'You need to be patreon to use this command.') 
    elif command == 'faccept':
        if config.premium:
            user.accept_friend_requests()
        else:
            print(Fore.RED + Style.BRIGHT + 'You need to be patreon to use this command.') 
    
    elif command == 'island':
        # Exécution pour les IDs [1, 2, 3] en une seule requête
        user.reward_gather_island([1, 2, 3])
        # Exécution séparée pour les IDs 5, 6 et 7
        for facility_id in [4, 5, 6, 7]:
            accepted = user.reward_gather_island([facility_id])
        if accepted == True:
            print(Fore.GREEN + Style.BRIGHT +"Gather island reward accepted.")
        else:
            print(Fore.RED + Style.BRIGHT + "No reward...")

    elif command == 'pka':
        user.get_trail_events()
    elif command == 'box':
        user.box_banner()
    elif command == 'stage':
        if stage is None or times is None:
            print(Fore.RED + Style.BRIGHT + 'Usage: stage stage_id times')
            return
        if stage.isdigit() and int(stage) not in consts.ban_id:
            for _ in range(int(times)):
                farm.complete_stage(str(stage))
        else:
            print(Fore.RED + Style.BRIGHT + "Invalid stage or banned stage.")
    
    elif command == 'autoteam':
        if config.premium:
            if type_color is None:
                print(Fore.RED + Style.BRIGHT + 'Usage: autoteam str')
                return
            if type_color == 'str':
                user.autoteam(None,pui=True)
            elif type_color == 'qck':
                user.autoteam(None,qck=True)
            elif type_color == 'dex':
                user.autoteam(None,dex=True)
            elif type_color == 'psy':
                user.autoteam(None,psy=True)
            elif type_color == 'int':
                user.autoteam(None,intel=True)
            else:
                print(Fore.RED + Style.BRIGHT + "Invalid command.")
        else:
            print(Fore.RED + Style.BRIGHT + 'You need to be patreon to use this command.') 

    elif command == 'custom':
        if config.premium:
            try:
                custom_files = [f for f in os.listdir('custom') if f.endswith('.txt')]
                
                if not custom_files:
                    print(Fore.RED + Style.BRIGHT + 'No custom command files found in "custom" folder.')
                else:
                    print(Fore.YELLOW + Style.BRIGHT + 'Available custom command files:')
                    for idx, file_name in enumerate(custom_files, start=1):
                        print(f'{idx}. {file_name}')
                    
                    selected_idx = input('Enter the number of the file you want to execute: ')
                    if selected_idx.isdigit() and 1 <= int(selected_idx) <= len(custom_files):
                        selected_file = custom_files[int(selected_idx) - 1]
                        
                        with open(os.path.join('custom', selected_file), 'r') as selected_custom_file:
                            custom_commands = selected_custom_file.read().splitlines()

                        for custom_command in custom_commands:
                            parts = custom_command.split()  # Split the command into parts
                            command = parts[0]
                            stage = None
                            times = None
                            type_color = None
                            if command == 'stage':
                                if len(parts) == 3:
                                    stage = parts[1]
                                    times = parts[2]
                                else:
                                    print(Fore.RED + Style.BRIGHT + 'Usage: stage stage_id times')
                                    continue  
                            if command == 'autoteam':
                                if len(parts) == 2:
                                    type_color = parts[1]
                                else:
                                    print(Fore.RED + Style.BRIGHT + 'Usage: autoteam str')
                                    continue  
                            user_command_executor(command, stage, times, type_color)
                    else:
                        print(Fore.RED + Style.BRIGHT + 'Invalid selection.')
            except FileNotFoundError:
                print(Fore.RED + Style.BRIGHT + 'Custom commands folder not found.')
        else:
            print(Fore.RED + Style.BRIGHT + 'You need to be patreon to use this command.') 
    else:
        print(Fore.RED + Style.BRIGHT + 'Command not found.')
