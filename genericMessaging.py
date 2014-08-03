__author__ = 'Poseidon'

# Import the AW SDK Information
from ctypes import *
aw = CDLL("aw")
AWEVENT = CFUNCTYPE(None)
AWCALLBACK = CFUNCTYPE(None)


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

# A generic HUD message function. Call this inside of other functions as necessary
def py_hud_generic(session, message, hud_id, hud_origin, location_x, location_y):
    aw.aw_int_set(422, 0)
    aw.aw_string_set(430, message)  # HUD Element Text and string
    aw.aw_int_set(423, hud_id)  # HUD Element ID
    aw.aw_int_set(428, 1)  # HUD Element Z
    aw.aw_int_set(424, session)  # Session Information
    aw.aw_int_set(427, location_y)  # HUD Element Y
    aw.aw_int_set(426, location_x)  # HUD Element X
    aw.aw_int_set(429, 0x0001)  # HUD_Element_Flags
    aw.aw_int_set(425, hud_origin)  # HUD Element Origin
    aw.aw_int_set(433, 300)  # HUD ELEMENT SIZE X
    aw.aw_int_set(434, 300)  # HUD ELEMENT SIZE Y
    aw.aw_int_set(431, 0xFFFF00)  # HUD COLOR
    aw.aw_float_set(432, c_float(1))
    aw.aw_hud_create()
    return
