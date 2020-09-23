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
# import board
import displayio
from adafruit_featherwing import minitft_featherwing
from adafruit_display_text import label
import terminalio
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.triangle import Triangle

"""Standard colors"""
WHITE = 0xFFFFFF
BLACK = 0x000000
RED = 0xFF0000
ORANGE = 0xFFA500
YELLOW = 0xFFFF00
GREEN = 0x00FF00
BLUE = 0x0000FF
PURPLE = 0x800080
PINK = 0xFFC0CB


minitft = minitft_featherwing.MiniTFTFeatherWing()

# Create a bitmap with seven colors
bitmap = displayio.Bitmap(minitft.display.width, minitft.display.height, 8) 

# Create a 5 color palette
palette = displayio.Palette(8)
palette[0] = BLACK
palette[1] = RED
palette[2] = ORANGE
palette[3] = YELLOW
palette[4] = GREEN
palette[5] = PINK
palette[6] = WHITE
palette[7] = BLUE

# Create a TileGrid using the Bitmap and Palette
tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)

# Create a Group
group = displayio.Group(max_size=10) 

# Add the TileGrid to the Group
group.append(tile_grid)

# Add the Group to the Display
minitft.display.show(group)

textbox_1 = label.Label(terminalio.FONT, text= "", max_glyphs=36, color=YELLOW, x=2, y=2)
group.append(textbox_1)
textbox_1.text = "Line Follower Menu";

textbox_2 = label.Label(terminalio.FONT, text= "", max_glyphs=36, color=WHITE, x=8, y=16)
group.append(textbox_2)
textbox_2.text = "LEFT - Calibrate Sensors";

textbox_3 = label.Label(terminalio.FONT, text= "", max_glyphs=36, color=WHITE, x=8, y=28)
group.append(textbox_3)
textbox_3.text = "RIGHT - Check Sensors";

textbox_4 = label.Label(terminalio.FONT, text= "", max_glyphs=36, color=PINK, x=8, y=40)
group.append(textbox_4)
textbox_4.text = "A - Start Driving";

textbox_5 = label.Label(terminalio.FONT, text= "", max_glyphs=36, color=WHITE, x=8, y=52)
group.append(textbox_5)
textbox_5.text = "B - Setup Parameters";

textbox_6 = label.Label(terminalio.FONT, text= "", max_glyphs=36, color=GREEN, x=2, y=66)
group.append(textbox_6)
textbox_6.text = "Next Run #: 1";

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
