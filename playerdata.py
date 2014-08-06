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
       #  print "Player Session {}".format(player_session)

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

def add_to_inventory(item, player_session):
    player_name = session_dict[player_session]
    genericMessaging.py_console(player_session, "Added {} to your inventory, {}!" .format(item, player_name))
    cursor.execute('''SELECT inventory FROM players WHERE name = ?''', (player_name,))
    inventory_current_row = cursor.fetchone()
    if inventory_current_row:
        cursor.execute('''UPDATE players SET inventory = ? WHERE name = ?''', (item, player_name,))
        db.commit()


def stat_change(session, stat, amount):
    target_session = session
    player_name = session_dict[target_session]

    # Select the appropriate stat for the player
    cursor.execute("SELECT %s FROM players where name=?" % (stat), (player_name,))
    stat_current_row = cursor.fetchone()
    if stat_current_row:
        stat_current = stat_current_row[0]
        stat_new = stat_current + amount
        print stat_current
        print stat_new

        # Update the player's appropriate stat by the given amount
        cursor.execute('''UPDATE players SET %s = ? WHERE name = ?''' % (stat), (stat_new, player_name,))
        db.commit()
        update_stats(session)


# Update the Stats HUD on demand
def update_stats(player_session):
    hud_id = 1000
    player_name = session_dict[player_session]
    hud_origin = 0
    location_x = 0
    location_y = 0
    cursor.execute('''SELECT name, health, mana, race FROM players WHERE name = ?''', (player_name,))
    results = cursor.fetchone()
    if results is not None:
        aw.aw_hud_destroy(player_session, hud_id)
        health = results[1]
        mana = results[2]
        race = results[3]
        genericMessaging.py_hud_generic(player_session, "Health: {}, Mana: {}, Race: {}".format(health, mana, race),
                                        1000,
                                        hud_origin, location_x, location_y)
    else:
        pass


    # Handle player damage
def damage_player(clicked_session):
    health_reduction = 10
    player_name = session_dict[clicked_session]

    cursor.execute('''SELECT name FROM players WHERE name = ?''', (player_name,))
    player_exists = cursor.fetchone()

    # Check the DB to verify the clicked player exists in the DB
    if player_exists:
        genericMessaging.py_console(clicked_session, "{} you just got hit!".format(player_name))
        cursor.execute('''SELECT name, health, mana, race FROM players WHERE name = ?''', (player_name,))
        results = cursor.fetchone()
        if results is not None:
            stat = "health"
            amount = health_reduction
            # print "{} was attacked!" .format(player_name)
            stat_change(clicked_session, stat, amount)
        else:
            pass
