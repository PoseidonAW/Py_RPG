# Setup ctypes and bring in the AW DLL for use.
from ctypes import *

# Create or open an existing SQLite DB
import sqlite3

db = sqlite3.connect('awrpg.db')
print "Opened database successfully"

cursor = db.cursor()
cursor.execute('''
CREATE TABLE players(id INTEGER PRIMARY KEY, name TEXT, health INTEGER, mana INTEGER, race TEXT)
''')
db.commit()
print "Chanes to awrpg db committed."


aw = CDLL("aw")

import time

# Set the return type for some functions that will be used.
aw.aw_string.restype = c_char_p

# Define a callback class for aw events.
AWEVENT = CFUNCTYPE(None)
AWCALLBACK = CFUNCTYPE(None)

# Main stuff
# Initialize the SDK
aw.aw_init(100)  # Change this to whatever build number is most current.

# Login function
def login():
    print "Please enter the bot name: "
    name = raw_input()
    print "Please enter your citnumber: "
    owner = int(raw_input())
    print "Please enter your PPW: "
    password = raw_input()
    aw.aw_string_set(0, name)
    aw.aw_int_set(2, owner)
    aw.aw_string_set(3, password)
    aw.aw_login()


print 'Avatar Add'

bot_owner = "Poseidon"

# Create a dictionary to keep track of names and matching session information
# Since the SDK is a little fickle.
session_dict = {}

time = time.asctime(time.localtime(time.time()))

# Handle Player Registration
def player_registration(player_name, player_session):
    player = player_name
    # Access the DB and determine if the user has a player account
    cursor.execute('''SELECT name FROM players WHERE name = ?''', (player,))
    player_exists = cursor.fetchone()
    if player_exists:
        aw.aw_say("You already have an account")
        print "You already have an account!"

    # If no account exists, create a new DB entry with the player's name
    else:
        hud_origin = 0
        location_x = 0
        location_y = 0
        health = 1000.0
        mana = 250.0
        race = "Human"

        cursor.execute('''INSERT INTO players(name, health, mana, race)
                            VALUES(?,?,?,?)''', (player, health, mana, race))
        db.commit()
        print 'Player added: ' + player
        aw.aw_say("Welcome to the club, " + player)
        py_hud_generic(player_session, "Health: {}, Mana: {}, Race: {}".format(health, mana, race), 1000,
                        hud_origin, location_x, location_y)

def py_chat():

    return

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
        py_hud_generic(player_session, "Health: {}, Mana: {}, Race: {}".format(health, mana, race), 1000,
                        hud_origin, location_x, location_y)
    else:
        pass

# Handle conditions where a player clicks a HUD item
def py_hud_click():
    session_number = aw.aw_int(424)
    hud_id = aw.aw_int(423)
    session_name = session_dict[session_number]
    # aw.aw_say(session_name + " (session number: " + str(session_number) + ")" + " clicked HUD " + str(hud_id))

    # If the player clicks the "Register" HUD, call player_registration
    if hud_id == 1001:
        player_registration(session_name, session_number)
        aw.aw_hud_destroy(session_number, hud_id)

    # If the player clicks their Stats HUD, send them a message
    if hud_id == 1000:
        py_console(session_number,
                   "{} that's your stats HUD - You can't close it! (but maybe I'll add that as a feature =-)".format(
                       session_name))
        return

    # Handle HUD clicks on the "Damage Indicator" flash
    if hud_id == 001:
        aw.aw_hud_destroy(session_number, hud_id)

    else:
        aw.aw_hud_destroy(session_number, hud_id)

    return


def py_hud_generic(session, message, hud_id, hud_origin, location_x, location_y):
    """

    :rtype : Creates a HUD for the noted session
    """
    av_session = session
    aw.aw_int_set(422, 0)
    aw.aw_string_set(430, message)  # HUD Element Text and string
    aw.aw_int_set(423, hud_id)  # HUD Element ID
    aw.aw_int_set(428, 1)  # HUD Element Z
    aw.aw_int_set(424, av_session)  # Session Information
    aw.aw_int_set(427, location_y)  # HUD Element Y
    aw.aw_int_set(426, location_x)  # HUD Element X
    aw.aw_int_set(429, 0x0001)  # HUD_Element_Flags
    aw.aw_int_set(425, hud_origin)  # HUD Element Origin
    aw.aw_int_set(433, 300)  # HUD ELEMENT SIZE X
    aw.aw_int_set(434, 300)  # HUD ELEMENT SIZE Y
    aw.aw_int_set(431, 0xFFFF00)  # HUD COLOR
    aw.aw_float_set(432, c_float(1))
    aw.aw_hud_create()
    rc = aw.aw_hud_create()
    print rc
    return

# Handle player damage
def damage_player(clicked_session):
    health_reduction = 10
    player_name = session_dict[clicked_session]

    cursor.execute('''SELECT name FROM players WHERE name = ?''', (player_name,))
    player_exists = cursor.fetchone()

    # Check the DB to verify the clicked player exists in the DB
    if player_exists:
        py_console(clicked_session, "{} you just got hit!".format(player_name))
        hud_origin = 0
        location_x = 0
        location_y = 0
        cursor.execute('''SELECT name, health, mana, race FROM players WHERE name = ?''', (player_name,))
        results = cursor.fetchone()
        if results is not None:
            stat = "health"
            amount = health_reduction
            print "{} was attacked!" .format(player_name)
            stat_change(clicked_session, stat, amount)
        else:
            pass


def py_avatar_click():
    av_session = aw.aw_int(206)
    player_name = session_dict[av_session]
    clicked_session = aw.aw_int(285)
    clicked_name = session_dict[clicked_session]

    # Initialize a variable that allows combat in the world.
    combat = 1

    if combat == 1:
        damage_player(clicked_session) # Damage the player who was clicked
        py_hud_damage(clicked_session) # Activate that damage indicator HUD



    else:
        pass

    return

def py_hud_destroy(session, hud_id):
    aw.aw_hud_destroy(session, hud_id)
    return

def py_hud_damage(session):
    hud_id = 001
    aw.aw_int_set(422, 1)
    aw.aw_string_set(430, "red.jpg")  # HUD Element Text and string
    aw.aw_int_set(433, 2000) # size
    aw.aw_int_set(434, 2000) # size
    aw.aw_int_set(423, hud_id)  # HUD Element ID
    aw.aw_int_set(424, session)  # Session Information
    aw.aw_int_set(429, 0x0002)  # HUD_Element_Flags
    aw.aw_int_set(432, 0xFFFFFF)
    aw.aw_int_set(429, 0x0001)  # HUD_Element_Flags
    aw.aw_float_set(432, c_float(.8))
    aw.aw_hud_create()
    py_hud_destroy(session, 001)
    return


def py_object_bump():
    print "Someone bumped something"
    session = aw.aw_int(206)
    py_console(session, 'You bumped something')


def check_player_status(av_session):
    # Check to see if the new user exists in the player database
    player_name = session_dict[av_session]
    player_session = av_session
    cursor.execute('''SELECT name FROM players WHERE name = ?''', (player_name,))
    player_exists = cursor.fetchone()

    if player_exists:
        py_console(player_session, "Welcome back to the game, {}".format(player_name))
        print "{} has returned".format(player_name)
        hud_origin = 0
        location_x = 0
        location_y = 0
        cursor.execute('''SELECT name, health, mana, race FROM players WHERE name = ?''', (player_name,))
        results = cursor.fetchone()
        if results is not None:
            health = results[1]
            mana = results[2]
            race = results[3]
            py_hud_generic(player_session, "Health: {}, Mana: {}, Race: {}".format(health, mana, race), 1000,
                           hud_origin, location_x, location_y)
        else:
            pass

    else:
        hud_origin = 4
        location_x = -100
        location_y = -100
        py_hud_generic(player_session, "Register", 1001, hud_origin, location_x, location_y)
        print "Inviting {} to the game".format(player_name)


def py_avatar_add():
    av_session = aw.aw_int(206)
    player_name = aw.aw_string(207)
    session_dict[av_session] = player_name

    print player_name
    print av_session
    print session_dict

    # Sends users a message when they first enter the world
    py_console(av_session, "You've arrived inside Jim's lab. Expect chaos.")
    # Check to see if the person has an account
    check_player_status(av_session)
    # py_console(player_session, "It looks like you're new around here, {}. If you'd like "
    #"to join the game, simply say 'Register'" .format(player_name))

    return


def py_avatar_delete():
    player_name = aw.aw_string(207)
    player_session = aw.aw_int(206)
    session_dict.pop(player_session)


# A generic console message function. Call this inside of other functions as necessary
def py_console(session, message):
    target_session = session
    aw.aw_int_set(329, 255)
    aw.aw_int_set(330, 0)
    aw.aw_int_set(331, 0)
    aw.aw_int_set(332, 1)
    aw.aw_int_set(333, 1)
    aw.aw_string_set(334, message)
    # aw.aw_int_set(206, target_session)
    aw.aw_console_message(target_session)
    return

def stat_change(session, stat, amount):
    target_session = session
    player_name = session_dict[target_session]
    print "Modifying {}'s {} by {}" .format(player_name, stat, amount)
    mana_addition = amount
    target_stat = stat

    if target_stat == "health":
        cursor.execute('''SELECT health FROM players WHERE name = ?''', (player_name,))
        health_current_row = cursor.fetchone()
        if health_current_row is not None:
            health_current = health_current_row[0]
            new_health = health_current - amount
            cursor.execute('''UPDATE players SET health = ? WHERE name = ?''', (new_health, player_name,))
            db.commit()
            update_stats(session)
            print health_current
        else:
            pass

    if target_stat == "mana":
        cursor.execute('''SELECT mana FROM players WHERE name = ?''', (player_name,))
        mana_current_row = cursor.fetchone()
        if mana_current_row is not None:
            mana_current = mana_current_row[0]
            new_mana = mana_current + mana_addition
            cursor.execute('''UPDATE players SET mana = ? WHERE name = ?''', (new_mana, player_name,))
            db.commit()
            update_stats(session)
            print mana_current
        else:
            pass


def py_object_click():
    session = aw.aw_int(206)
    av_session = aw.aw_int(206)
    if aw.aw_string(240) >= "~mana:":
        py_console(session, "Here's some mana!")
        stat = "mana"
        amount = 50
        print "{} is now {}" .format(stat, amount)
        stat_change(av_session, stat, amount)

        # if aw.aw_int(244) == 293157:
        #py_hud_generic(session, "Don't touch Poseidon's things.")
        #return


# def py_avatar_add():
# session = aw.aw_int(206)
# aw.aw_say("Hi there! You have session number " + str(session))
# print session
# session = session_id(aw.aw_int(206))
# hud_create = AWEVENT(py_hud(session))
#hud_text = aw.aw_int_set(422, hud_create)
#py_hud(session)

# Create an instance
rc1 = aw.aw_create(0, 0, 0)
# if rc1>0:
print 'AW_Create:'
print rc1

# Set events
# Avatar Add Event
avatar_add = AWEVENT(py_avatar_add)
aw.aw_event_set(0, avatar_add)

# Avatar Delete Event
avatar_delete = AWEVENT(py_avatar_delete)
aw.aw_event_set(2, avatar_delete)

# Chat Event
chat = AWEVENT(py_chat)
aw.aw_event_set(6, chat)

# HUD Click Event
hud_click = AWEVENT(py_hud_click)
aw.aw_event_set(47, hud_click)

# An avatar is clicked
avatar_click = AWEVENT(py_avatar_click)
aw.aw_event_set(20, avatar_click)

# Console message sent
console_message = AWEVENT(py_console)
aw.aw_event_set(29, console_message)

# Object Bump Event
object_bump = AWEVENT(py_object_bump)
aw.aw_event_set(38, object_bump)

# Object is clicked
object_click = AWEVENT(py_object_click)
aw.aw_event_set(18, object_click)

# Log the bot in
login()

# Enter a world at GZ
aw.aw_bool_set(328, 1)
rc2 = aw.aw_enter("AWRPG2")
# if rc2>0:
print 'AW_ENTER:'
print rc2

aw.aw_int_set(198, 0)
aw.aw_int_set(199, 0)
aw.aw_int_set(200, 0)
rc3 = aw.aw_state_change()
# if rc3>0:
print 'STATE_CHANGE:'
print rc3

# Loop off into infinity
while 1:
    aw.aw_wait(-1)