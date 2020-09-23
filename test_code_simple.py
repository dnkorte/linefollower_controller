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

# create instance for TFT board
minitft = minitft_featherwing.MiniTFTFeatherWing()

for i in range(30):
	print(i)
	time.sleep(1)
