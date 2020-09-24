"""
# Controller for Line-Following Robot
# This runs on an Adafruit Feather M4, with a MiniTFT board.  
# It drives a TB6612 to control 2 DC Motors (in blue servo case)
# and talks over I2C to an ItsyBitsy that interfaces a Pololu 
# line following sensor
#
# Author(s): Don Korte
# Module:  screen_menu.py generates and manages framework to display main menu
# github: https://github.com/dnkorte/linefollower_controller
#
# Reference: https://circuitpython.readthedocs.io/projects/featherwing/en/latest/_modules/adafruit_featherwing/minitft_featherwing.html
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
from adafruit_display_text import label
import terminalio
import displayio
import time

import mycolors

class Screen_Menu:
	def __init__(self, tft_device, menu_items, device_linesense):
		self.this_tft = tft_device
		self.menu_items = menu_items
		self.num_of_menu_items = len(menu_items)
		self.first_item_to_show = 0
		self.currently_selected_list_item = 0
		self.device_linesense = device_linesense

		self.this_group = displayio.Group(max_size=10) 

		self.textbox_1 = label.Label(terminalio.FONT, text= "", max_glyphs=36, color=mycolors.YELLOW, x=2, y=0)
		self.this_group.append(self.textbox_1)

		self.textbox_2 = label.Label(terminalio.FONT, text= "", max_glyphs=36, color=mycolors.YELLOW, x=2, y=14)
		self.this_group.append(self.textbox_2)

		self.textbox_3 = label.Label(terminalio.FONT, text= "", max_glyphs=36, color=mycolors.GRAY, x=12, y=28)
		self.this_group.append(self.textbox_3)

		self.textbox_4 = label.Label(terminalio.FONT, text= "", max_glyphs=36, color=mycolors.GRAY, x=12, y=40)
		self.this_group.append(self.textbox_4)

		self.textbox_5 = label.Label(terminalio.FONT, text= "", max_glyphs=36, color=mycolors.GRAY, x=12, y=52)
		self.this_group.append(self.textbox_5)

		self.textbox_6 = label.Label(terminalio.FONT, text= "", max_glyphs=36, color=mycolors.GRAY, x=12, y=66)
		self.this_group.append(self.textbox_6)

		self.textbox_cal = label.Label(terminalio.FONT, text= "", max_glyphs=6, color=mycolors.RED, x=130, y=0)
		self.this_group.append(self.textbox_cal)

		self.textbox_3.text = self.menu_items[0][0]
		self.textbox_3.color = mycolors.WHITE
		self.textbox_4.text = self.menu_items[1][0]
		self.textbox_5.text = self.menu_items[2][0]
		self.textbox_6.text = self.menu_items[3][0]

	def show_this_screen(self):
		self.this_tft.display.show(self.this_group)

	# this function initiates mode, runs it till done, then returns text string indicating next mode
	def run_menu(self):
		self.show_this_screen()
		self.textbox_1.text = "UP / DOWN to scroll";
		self.textbox_2.text = "Click A to select"

		if (self.device_linesense.calibrate_check()):
			self.textbox_cal.text = "  CAL"
			self.textbox_cal.color = mycolors.GREEN
		else:
			self.textbox_cal.text = "NOCAL"
			self.textbox_cal.color = mycolors.RED

		while True:
			# note possibilities are buttons.up buttons.down buttons.left buttons.right buttons.select buttons.a buttons.b
			buttons = self.this_tft.buttons

			mustScrollDisplay = False
			if buttons.up:
			    # print("Button UP!")
			    still_pressed = True
			    while  still_pressed:
			    	buttons = self.this_tft.buttons
			    	still_pressed = buttons.up
			    	time.sleep(0.05)
			    # print("released")
			    self.currently_selected_list_item -= 1
			    if (self.currently_selected_list_item < 0):
			    	self.currently_selected_list_item = self.num_of_menu_items - 1

			elif buttons.down:
			    # print("Button Down!")
			    still_pressed = True
			    while  still_pressed:
			    	buttons = self.this_tft.buttons
			    	still_pressed = buttons.down
			    	time.sleep(0.05)
			    # print("released")
			    self.currently_selected_list_item += 1
			    if (self.currently_selected_list_item >= self.num_of_menu_items):
			    	self.currently_selected_list_item = 0

			elif buttons.a:
			    # print("Button A!")
			    still_pressed = True
			    while  still_pressed:
			    	buttons = self.this_tft.buttons
			    	still_pressed = buttons.a
			    	time.sleep(0.05)
			    # print("released")
			    # print("returning: ", self.menu_items[self.currently_selected_list_item][1])
			    return self.menu_items[self.currently_selected_list_item][1]

			else:
				pass

			self.textbox_3.color = mycolors.GRAY
			self.textbox_4.color = mycolors.GRAY
			self.textbox_5.color = mycolors.GRAY
			self.textbox_6.color = mycolors.GRAY

			if (self.currently_selected_list_item - self.first_item_to_show >= 4):
				# self.first_item_to_show = self.currently_selected_list_item - 4
				self.first_item_to_show += 1
				mustScrollDisplay = True

			if (self.currently_selected_list_item - self.first_item_to_show < 0):
				# self.first_item_to_show = self.currently_selected_list_item - 4
				self.first_item_to_show -= 1
				mustScrollDisplay = True

			# now if we moved beyond the 4 showable items, scroll the list on display
			if (mustScrollDisplay):
				self.textbox_3.text = self.menu_items[self.first_item_to_show + 0][0]

				if (self.first_item_to_show + 1 < self.num_of_menu_items):
					self.textbox_4.text = self.menu_items[self.first_item_to_show + 1][0]
				else:
					self.textbox_4.text = ""

				if (self.first_item_to_show + 2 < self.num_of_menu_items):
					self.textbox_5.text = self.menu_items[self.first_item_to_show + 2][0]
				else:
					self.textbox_5.text = ""

				if (self.first_item_to_show + 3 < self.num_of_menu_items):
					self.textbox_6.text = self.menu_items[self.first_item_to_show + 3][0]
				else:
					self.textbox_6.text = ""

			# and finally, adjust the red highlight to put it on current item
			if ((self.first_item_to_show + 0) == self.currently_selected_list_item):
				self.textbox_3.color = mycolors.WHITE

			if ((self.first_item_to_show + 1) == self.currently_selected_list_item):
				self.textbox_4.color = mycolors.WHITE

			if ((self.first_item_to_show + 2) == self.currently_selected_list_item):
				self.textbox_5.color = mycolors.WHITE

			if ((self.first_item_to_show + 3) == self.currently_selected_list_item):
				self.textbox_6.color = mycolors.WHITE

			time.sleep(0.1)