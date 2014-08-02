__author__ = 'Poseidon'

# Import the AW SDK Information
from ctypes import *

aw = CDLL("aw")
AWEVENT = CFUNCTYPE(None)
AWCALLBACK = CFUNCTYPE(None)

import sqlite3
import genericMessaging

db = sqlite3.connect('awrpg.db')
cursor = db.cursor()

from random import randint

session_dict = {}


def player_check(player_session):
    player = session_dict[player_session]

    # Access the DB and determine if the user has a player account
    cursor.execute('''SELECT name FROM players WHERE name = ?''', (player,))
    player_exists = cursor.fetchone()
    if player_exists:
        player_status = True

    else:
        player_status = False

    return player_status


class Character:
    def __init__(self):
        self.name = ""
        self.health = 1
        self.mana = 1
        self.race = "Human"

    def player_registration(self, player_session):
        player = session_dict[player_session]
        print "Player Session {}".format(player_session)

        cursor.execute('''SELECT name FROM players WHERE name = ?''', (player,))
        player_exists = cursor.fetchone()

        if not player_exists:
            hud_origin = 0
            location_x = 0
            location_y = 0
            health = self.health
            mana = self.mana
            race = self.race

            cursor.execute('''INSERT INTO players(name, health, mana, race)
                                VALUES(?,?,?,?)''', (player, health, mana, race))
            db.commit()
            print 'Player added: ' + player
            aw.aw_say("Welcome to the club, " + player)
            genericMessaging.py_hud_generic(player_session, "Health: {}, Mana: {}, Race: {}".format(health, mana, race),
                                            1000,
                                            hud_origin, location_x, location_y)


        else:
            return

class Immortal(Character):
    def __init__(self):
        Character.__init__(self)
        self.state = 'normal'
        self.health = 10000
        self.race = "Immortal"

        return
