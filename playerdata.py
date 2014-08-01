__author__ = 'Poseidon'

# Import the AW SDK Information
from ctypes import *
aw = CDLL("aw")
AWEVENT = CFUNCTYPE(None)
AWCALLBACK = CFUNCTYPE(None)

import sqlite3
db = sqlite3.connect('awrpg.db')
cursor = db.cursor()



def player_check(cit_name):
    player = cit_name

    # Access the DB and determine if the user has a player account
    cursor.execute('''SELECT name FROM players WHERE name = ?''', (player,))
    player_exists = cursor.fetchone()
    if player_exists:
        player_status = True

    else:
        player_status = False

    return player_status