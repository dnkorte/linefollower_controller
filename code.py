"""
code_circuitpython/line_follower_main/controller.py
 
note that if you use displayio functions in the "normal" way, then they over-ride
the console style scrolling printout for print(xxx) on the TFT screen,
but the print commands still work for the the attached serial terminal.
  
this example is generated in part from TFT guide: 
   https://learn.adafruit.com/adafruit-mini-tft-featherwing/mini-color-tft-with-joystick-featherwing
and verifies operation of board, and shows use of "console print" feature
"""

import time
from adafruit_featherwing import minitft_featherwing

# from mode_mainmenu import Mode_MainMenu
from screen_menu import Screen_Menu
from screen_dashboard import Screen_Dashboard
from mode_config import Mode_Config
from mode_followpath import Mode_FollowPath
from mode_driveshapes import Mode_DriveShapes
from mode_calibrate import Mode_Calibrate
from mode_config import Mode_Config
from device_motors import Device_Motors
from device_linesense import Device_LineSense
from device_storage import Device_Storage


# create instance for TFT board
# (note it is possible that the TFT board itself doesn't have any
# pullups for the I2C pins used for SeeSaw -- if you use it without
# including pullups, the display shows letters but this driver initialization
# never completes...)
minitft = minitft_featherwing.MiniTFTFeatherWing()

# create / initialize device handlers
screen_dashboard = Screen_Dashboard(minitft)
device_motors = Device_Motors(screen_dashboard)
device_linesense = Device_LineSense(screen_dashboard)
device_storage = Device_Storage()

# create instances of mode handlers
# 
# mode_mainmenu = Mode_MainMenu(minitft, device_motors, device_linesense, device_storage)
#mainmenu_items = [ ["Calibrate Sensors", "CAL"], ["Follow Path", "PATH"], ["Drive Straight 100 cm", "STRAIGHT"], 
#    ["Curve Left", "CURVLEFT"], ["Curve Right", "CURVRIGHT"], ["Square Left", "SQLEFT"], 
#    ["Square Right", "SQRIGHT"], ["Display Linesensor", "DISPSENS"] ]
#    
mainmenu_items = [ ["Calibrate Sensors", "CAL"], ["Follow Path", "PATH"], 
    ["Setup Parameters", "SETUP"], ["Display Linesensor", "DISPSENS"] ]
screen_menu = Screen_Menu(minitft, mainmenu_items, device_linesense)

mode_followpath = Mode_FollowPath(screen_dashboard, device_motors, device_linesense, device_storage)
mode_driveshapes = Mode_DriveShapes(screen_dashboard, device_motors, device_linesense, device_storage)
mode_calibrate = Mode_Calibrate(screen_dashboard, device_motors, device_linesense, device_storage)
mode_config = Mode_Config(minitft, mode_followpath)

next_mode = "MAINMENU"
while True:
    if (next_mode == "PATH"):
        next_mode = mode_followpath.run_mode()
        next_mode="MAINMENU"

    elif (next_mode == "CAL"):
        next_mode = mode_calibrate.run_mode()
        next_mode="MAINMENU"

    elif (next_mode == "SETUP"):
        next_mode = mode_config.run_mode()
        next_mode="MAINMENU"

    elif (next_mode == "STRAIGHT"):
        next_mode = mode_driveshapes.run_straight()
        next_mode="MAINMENU"

    elif (next_mode == "CURVLEFT"):
        next_mode = mode_driveshapes.run_curveleft()
        next_mode="MAINMENU"

    elif (next_mode == "CURVRIGHT"):
        next_mode = mode_driveshapes.run_curveright()
        next_mode="MAINMENU"

    elif (next_mode == "DISPSENS"):
        next_mode = mode_calibrate.display_linesensor()
        next_mode="MAINMENU"
    else: 
        next_mode = screen_menu.run_menu()

    time.sleep(0.1)





