from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(["../src/deck_ship.py","../src/auth.py", "../src/database.py", "../src/config.py", "../src/consts.py", "../src/cryption.py", "../src/db.py", "../src/deck.py", "../src/events.py", "../src/farm.py", "../src/logsTransfer.py", "../src/optc.py",
                          "../src/quests.py", "../src/save_data.py", "../src/summon.py", "../src/transferConsts.py", "../src/tutorial.py", "../src/user.py", "../src/user_cmd.py", "../src/utils.py", "../src/webhook.py"])
)
