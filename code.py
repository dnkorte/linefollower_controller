"""
# Controller for Line-Following Robot
# This runs on an Adafruit Feather M4, with a MiniTFT board.  
# It drives a TB6612 to control 2 DC Motors (in blue servo case)
# and talks over I2C to an ItsyBitsy that interfaces a Pololu 
# line following sensor
#
# Author(s): Don Korte
# Module:  code.py is mainline initialization and master loop
# github: https://github.com/dnkorte/linefollower_controller
# 
# MIT License
# 
# Copyright (c) 2020 Don Korte
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 
"""

import time
from adafruit_featherwing import minitft_featherwing

# from mode_mainmenu import Mode_MainMenu
from screen_menu import Screen_Menu
from screen_dashboard import Screen_Dashboard
from screen_summary import Screen_Summary
from mode_config import Mode_Config
from mode_followpath import Mode_FollowPath
from mode_driveshapes import Mode_DriveShapes
from mode_calibrate import Mode_Calibrate
from mode_config import Mode_Config
from device_motors import Device_Motors
from device_linesense import Device_LineSense
from device_storage import Device_Storage
from device_battery import Device_Battery


# create instance for TFT board
# (note it is possible that the TFT board itself doesn't have any
# pullups for the I2C pins used for SeeSaw -- if you use it without
# including pullups, the display shows letters but this driver initialization
# never completes...)
minitft = minitft_featherwing.MiniTFTFeatherWing()

# create / initialize device handlers
mode_config = Mode_Config(minitft)
screen_dashboard = Screen_Dashboard(minitft, mode_config)
device_motors = Device_Motors(screen_dashboard)
device_linesense = Device_LineSense(screen_dashboard)
device_storage = Device_Storage()
device_battery = Device_Battery()

# create instances of mode handlers

mainmenu_items = [
    ["Calibrate Sensors", "CAL"],
    ["Follow Path", "PATH"],
    ["Setup Parameters", "SETUP"],
    ["Display Linesensor", "DISPSENS"],
]
screen_menu = Screen_Menu(minitft, mainmenu_items, device_linesense, device_battery)

mode_followpath = Mode_FollowPath(
    screen_dashboard, device_motors, device_linesense, device_storage, mode_config
)
mode_driveshapes = Mode_DriveShapes(
    screen_dashboard, device_motors, device_linesense, device_storage
)
mode_calibrate = Mode_Calibrate(
    screen_dashboard, device_motors, device_linesense, device_storage
)
screen_summary = Screen_Summary(
    minitft, mode_followpath, mode_config, device_storage, device_battery
)

next_mode = "MAINMENU"
while True:
    if next_mode == "PATH":
        mode_followpath.run_mode()
        screen_summary.run_mode()
        next_mode = "MAINMENU"

    elif next_mode == "CAL":
        next_mode = mode_calibrate.run_mode()
        next_mode = "MAINMENU"

    elif next_mode == "SETUP":
        next_mode = mode_config.run_mode()
        next_mode = "MAINMENU"

    elif next_mode == "STRAIGHT":
        next_mode = mode_driveshapes.run_straight()
        next_mode = "MAINMENU"

    elif next_mode == "CURVLEFT":
        next_mode = mode_driveshapes.run_curveleft()
        next_mode = "MAINMENU"

    elif next_mode == "CURVRIGHT":
        next_mode = mode_driveshapes.run_curveright()
        next_mode = "MAINMENU"

    elif next_mode == "DISPSENS":
        next_mode = mode_calibrate.display_linesensor()
        next_mode = "MAINMENU"
    else:
        next_mode = screen_menu.run_menu()

    time.sleep(0.1)
