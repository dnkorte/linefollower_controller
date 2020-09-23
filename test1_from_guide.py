# 
# code_circuitpython/line_follower_main/test1_from_guide.py
# 
# This example display a CircuitPython console and
# print which button that is being pressed if any
#  
# this example is from TFT guide: 
#    https://learn.adafruit.com/adafruit-mini-tft-featherwing/mini-color-tft-with-joystick-featherwing
# and verifies operation of board, and shows use of "console print" feature
# 


import time
from adafruit_featherwing import minitft_featherwing

minitft = minitft_featherwing.MiniTFTFeatherWing()

while True:
    buttons = minitft.buttons

    if buttons.right:
        print("Button RIGHT!")

    if buttons.down:
        print("Button DOWN!")

    if buttons.left:
        print("Button LEFT!")

    if buttons.up:
        print("Button UP!")

    if buttons.select:
        print("Button SELECT!")

    if buttons.a:
        print("Button A!")

    if buttons.b:
        print("Button B!")

    time.sleep(0.001)
