# Setup ctypes and bring in the AW DLL for use.
from ctypes import *
from playerdata import Character

# Create or open an existing SQLite DB
import sqlite3

import playerdata
import genericMessaging

session_dict = playerdata.session_dict
db = sqlite3.connect('awrpg.db')
# print "Opened database successfully"

cursor = db.cursor()
# cursor.execute('''
# CREATE TABLE players(id INTEGER PRIMARY KEY, name TEXT, health INTEGER, mana INTEGER, race TEXT, inventory TEXT)
# ''')
# db.commit()
# print "Chanes to awrpg db committed."


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

time = time.asctime(time.localtime(time.time()))

# Displays a list of current users in world
def list_current_users(player_session):
    temp = list()
    for i in session_dict.itervalues():
        temp.append(i)
    genericMessaging.py_console(player_session, str(temp))


def py_chat():
    player_session = aw.aw_int(222)
    if aw.aw_string(223) == "/who":
        list_current_users(player_session)

    if aw.aw_string(223) == "/inventory":
        player_name = session_dict[player_session]
        cursor.execute('''SELECT inventory FROM players WHERE name = ?''', (player_name,))
        player_inventory = cursor.fetchone()
        genericMessaging.py_console(player_session, str(player_inventory))


# Handle conditions where a player clicks a HUD item
def py_hud_click():
    session_number = aw.aw_int(424)
    hud_id = aw.aw_int(423)
    session_name = session_dict[session_number]
    # aw.aw_say(session_name + " (session number: " + str(session_number) + ")" + " clicked HUD " + str(hud_id))

    # If the player clicks the "Register" HUD, call player_registration
    if hud_id == 1001:
        aw.aw_hud_destroy(session_number, hud_id)

        hud_origin = 4
        human_location_x = 0
        human_location_y = -100
        immortal_location_x = -200
        immortal_location_y = -100
        genericMessaging.py_hud_generic(session_number, "Human", 2000, hud_origin, human_location_x, human_location_y)
        genericMessaging.py_hud_generic(session_number, "Immortal", 2001, hud_origin, immortal_location_x,
                                        immortal_location_y)

    if hud_id == 2000:
        playerdata.Character().player_registration(session_number)
        aw.aw_hud_destroy(session_number, hud_id)
        aw.aw_hud_destroy(session_number, 2001)

    if hud_id == 2001:
        playerdata.Immortal().player_registration(session_number)
        aw.aw_hud_destroy(session_number, hud_id)
        aw.aw_hud_destroy(session_number, 2000)

    # If the player clicks their Stats HUD, send them a message
    if hud_id == 1000:
        genericMessaging.py_console(session_number,
                                    "{} that's your stats HUD - You can't close it! (but maybe I'll add that as a feature =-)".format(
                                        session_name))
        return

    # Handle HUD clicks on the "Damage Indicator" flash
    if hud_id == 001:
        aw.aw_hud_destroy(session_number, hud_id)

    else:
        aw.aw_hud_destroy(session_number, hud_id)


def py_avatar_click():
    av_session = aw.aw_int(206)
    player_name = session_dict[av_session]
    clicked_session = aw.aw_int(285)
    clicked_name = session_dict[clicked_session]

    # Initialize a variable that allows combat in the world.
    combat = 1

    if combat == 1:
        playerdata.damage_player(clicked_session)  # Damage the player who was clicked
        py_hud_damage(clicked_session)  # Activate that damage indicator HUD



def py_hud_destroy(session, hud_id):
    aw.aw_hud_destroy(session, hud_id)


def py_hud_damage(session):
    hud_id = 001
    aw.aw_int_set(422, 1)
    aw.aw_string_set(430, "red.jpg")  # HUD Element Text and string
    aw.aw_int_set(433, 2000)  # size
    aw.aw_int_set(434, 2000)  # size
    aw.aw_int_set(423, hud_id)  # HUD Element ID
    aw.aw_int_set(424, session)  # Session Information
    aw.aw_int_set(429, 0x0002)  # HUD_Element_Flags
    aw.aw_int_set(432, 0xFFFFFF)
    aw.aw_int_set(429, 0x0001)  # HUD_Element_Flags
    aw.aw_float_set(432, c_float(.8))
    aw.aw_hud_create()
    py_hud_destroy(session, 001)


def py_object_bump():
    # print "Someone bumped something"
    session = aw.aw_int(206)
    genericMessaging.py_console(session, 'You bumped something')


def py_avatar_add():
    player_session = aw.aw_int(206)
    cit_name = aw.aw_string(207)
    playerdata.session_dict[player_session] = cit_name
    player_name = session_dict[player_session]

    # Store the player's name and session in a dictionary
    print playerdata.session_dict

    # Check to see if the player has an account
    player_check = playerdata.player_check(player_session)
    if player_check:
        genericMessaging.py_console(player_session, "Welcome back to the game, {}".format(player_name))
        # print "{} has returned".format(player_name)
        cursor.execute('''SELECT name, health, mana, race FROM players WHERE name = ?''', (player_name,))
        results = cursor.fetchone()

        # Create a HUD to display player stats
        hud_origin = 0
        location_x = 0
        location_y = 0
        health = results[1]
        mana = results[2]
        race = results[3]
        genericMessaging.py_hud_generic(player_session, "Health: {}, Mana: {}, Race: {}".format(health, mana, race),
                                        1000,
                                        hud_origin, location_x, location_y)

    # If the player does not exist, invite them to the game
    if not player_check:
        hud_origin = 4
        location_x = -100
        location_y = -100
        genericMessaging.py_hud_generic(player_session, "Register", 1001, hud_origin, location_x, location_y)
        # print "Inviting {} to the game".format(player_name)

    # Sends users a message when they first enter the world
    genericMessaging.py_console(player_session, "You've arrived inside Poseidon's lab. Expect chaos.")


def py_avatar_delete():
    player_session = aw.aw_int(206)
    # Remove the player's session and name information from session_dict
    session_dict.pop(player_session)

def py_object_click():
    av_session = aw.aw_int(206)
    action_description = aw.aw_string(240)
    description_start = action_description.find("~")
    description_end = action_description.find(":")
    command = action_description[description_start + 1:description_end]
    amount_end = action_description.find(";")
    amount = action_description[description_end + 1: amount_end]
    if command == "mana":
        stat = "mana"
        playerdata.stat_change(av_session, stat, int(amount))

    if command == "health":
        stat = "health"
        playerdata.stat_change(av_session, stat, int(amount))

    if aw.aw_string(240) == "inventory":
        item = aw.aw_string(238)
        playerdata.add_to_inventory(item, av_session)

def py_av_enter(avatar_add):
    #aw.aw_say("callback query")
    print 'callback av_enter'
    cit_name = aw.aw_string(30)
    aw.aw_say("Citizen added")
    print cit_name


# def py_avatar_add():
# session = aw.aw_int(206)
# aw.aw_say("Hi there! You have session number " + str(session))
# print session
# session = session_id(aw.aw_int(206))
# hud_create = AWEVENT(py_hud(session))
# hud_text = aw.aw_int_set(422, hud_create)
# py_hud(session)

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
console_message = AWEVENT(genericMessaging.py_console)
aw.aw_event_set(29, console_message)

# Object Bump Event
object_bump = AWEVENT(py_object_bump)
aw.aw_event_set(38, object_bump)

# Object is clicked
object_click = AWEVENT(py_object_click)
aw.aw_event_set(18, object_click)

av_enter = AWCALLBACK(py_av_enter)
aw.aw_callback_set(6, av_enter)

# Log the bot in
login()

# Enter a world at GZ
aw.aw_bool_set(328, 1)
rc2 = aw.aw_enter("AWRPG2")
aw.aw_hud_destroy()
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
    aw.aw_wait(1)
