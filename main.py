
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "../"))
import optc
from colorama import init, Fore, Style
# Coloroma autoreset
init(autoreset=True)


if __name__ == '__main__':
    
    print("\nNotice :\n"  "\
    You are free to use this program as you wish, however, we are not responsible for any actions\n\
    that your use may lead to (selling accounts, selling this program, etc.).\n\
    The main purpose is to simplify the farm of the game 'One Piece Treasure Cruise'.\n\
    This program is in beta, the features will be added as we go along and if users ask for it.\n\
    If you have any question feel free to ask in the discord server.\n\n" + \
    "We are NOT affiliated to Bandai Namco.\n\n")

    optc.start()



