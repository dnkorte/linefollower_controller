"""
# Controller for Line-Following Robot
# This runs on an Adafruit Feather M4, with a MiniTFT board.  
# It drives a TB6612 to control 2 DC Motors (in blue servo case)
# and talks over I2C to an ItsyBitsy that interfaces a Pololu 
# line following sensor
#
# Author(s): Don Korte
# Module:  mode_config.py generates and manages a menu that presents
#	various configuration parameters and allows user to change them
#	Note that the actual reading and setting of the parameters is 
#	handled by funcitons in the mode_followpath module
#
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

from adafruit_display_text import label
import terminalio
import displayio
import time

import mycolors

class Mode_Config:
	def __init__(self, tft_device, mode_followpath):
		self.this_tft = tft_device
		self.mode_followpath = mode_followpath
		self.currently_selected_list_item = 0
		self.first_item_to_show = 0
		self.currently_selected_list_item = 0
		self.menu_items = [ ["Throttle", "THR"], ["Loop Speed", "LPS"], ["Rxn Rate", "RR"]]
		self.num_of_menu_items = len(self.menu_items)

		self.this_group = displayio.Group(max_size=10) 

		self.textbox_1 = label.Label(terminalio.FONT, text= "", max_glyphs=36, color=mycolors.YELLOW, x=2, y=0)
		self.this_group.append(self.textbox_1)

		self.textbox_2 = label.Label(terminalio.FONT, text= "", max_glyphs=36, color=mycolors.YELLOW, x=2, y=14)
		self.this_group.append(self.textbox_2)

		self.textbox_3 = label.Label(terminalio.FONT, text= "", max_glyphs=36, color=mycolors.GRAY, x=12, y=28)
		self.this_group.append(self.textbox_3)

		self.textbox_3v = label.Label(terminalio.FONT, text= "", max_glyphs=36, color=mycolors.GRAY, x=100, y=28)
		self.this_group.append(self.textbox_3v)

		self.textbox_4 = label.Label(terminalio.FONT, text= "", max_glyphs=36, color=mycolors.GRAY, x=12, y=40)
		self.this_group.append(self.textbox_4)

		self.textbox_4v = label.Label(terminalio.FONT, text= "", max_glyphs=36, color=mycolors.GRAY, x=100, y=40)
		self.this_group.append(self.textbox_4v)

		self.textbox_5 = label.Label(terminalio.FONT, text= "", max_glyphs=36, color=mycolors.GRAY, x=12, y=52)
		self.this_group.append(self.textbox_5)

		self.textbox_5v = label.Label(terminalio.FONT, text= "", max_glyphs=36, color=mycolors.GRAY, x=100, y=52)
		self.this_group.append(self.textbox_5v)

		self.textbox_6 = label.Label(terminalio.FONT, text= "", max_glyphs=36, color=mycolors.YELLOW, x=2, y=66)
		self.this_group.append(self.textbox_6)

		self.textbox_3.text = self.menu_items[0][0]
		self.textbox_3.color = mycolors.WHITE
		self.textbox_4.text = self.menu_items[1][0]
		self.textbox_5.text = self.menu_items[2][0]

		self.textbox_3v.text = self._get_param(self.menu_items[0][1])
		self.textbox_3v.color = mycolors.WHITE
		self.textbox_4v.text = self._get_param(self.menu_items[1][1])
		self.textbox_5v.text = self._get_param(self.menu_items[2][1])


	def show_this_screen(self):
		self.this_tft.display.show(self.this_group)

	# this function initiates mode, runs it till done, then returns text string indicating next mode
	def run_mode(self):
		self.show_this_screen()
		self.textbox_1.text = "UP / DOWN select param";
		self.textbox_2.text = "LEFT / RIGHT chg param";
		self.textbox_6.text = "Click A to exit";

		while True:
			# note possibilities are buttons.up buttons.down buttons.left buttons.right buttons.select buttons.a buttons.b
			buttons = self.this_tft.buttons
			mustScrollDisplay = False
			mustUpdateValues = False

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

			elif buttons.left:
			    # print("Button Down!")
			    still_pressed = True
			    while  still_pressed:
			    	buttons = self.this_tft.buttons
			    	still_pressed = buttons.down
			    	time.sleep(0.05)
			    # print("released")
			    temp = self._scroll_param(self.menu_items[self.currently_selected_list_item][1], -1)
			    print(temp)
			    mustUpdateValues = True

			elif buttons.right:
			    # print("Button Down!")
			    still_pressed = True
			    while  still_pressed:
			    	buttons = self.this_tft.buttons
			    	still_pressed = buttons.down
			    	time.sleep(0.05)
			    # print("released")
			    temp = self._scroll_param(self.menu_items[self.currently_selected_list_item][1], +1)
			    print(temp)
			    mustUpdateValues = True

			elif buttons.a:
			    # print("Button A!")
			    still_pressed = True
			    while  still_pressed:
			    	buttons = self.this_tft.buttons
			    	still_pressed = buttons.a
			    	time.sleep(0.05)
			    # print("released")
			    # print("returning: ", self.menu_items[self.currently_selected_list_item][1])
			    return 

			else:
				pass

			self.textbox_3.color = mycolors.GRAY
			self.textbox_4.color = mycolors.GRAY
			self.textbox_5.color = mycolors.GRAY

			self.textbox_3v.color = mycolors.GRAY
			self.textbox_4v.color = mycolors.GRAY
			self.textbox_5v.color = mycolors.GRAY

			if (self.currently_selected_list_item - self.first_item_to_show >= 3):
				# self.first_item_to_show = self.currently_selected_list_item - 4
				self.first_item_to_show += 1
				mustScrollDisplay = True

			if (self.currently_selected_list_item - self.first_item_to_show < 0):
				# self.first_item_to_show = self.currently_selected_list_item - 4
				self.first_item_to_show -= 1
				mustScrollDisplay = True

			# now if we moved beyond the 3 showable items, scroll the list on display
			if (mustScrollDisplay or mustUpdateValues):
				self.textbox_3.text = self.menu_items[self.first_item_to_show + 0][0]
				self.textbox_3v.text = self._get_param(self.menu_items[self.first_item_to_show + 0][1])

				if (self.first_item_to_show + 1 < self.num_of_menu_items):
					self.textbox_4.text = self.menu_items[self.first_item_to_show + 1][0]
					self.textbox_4v.text = self._get_param(self.menu_items[self.first_item_to_show + 1][1])
				else:
					self.textbox_4.text = ""
					self.textbox_4v.text = ""

				if (self.first_item_to_show + 2 < self.num_of_menu_items):
					self.textbox_5.text = self.menu_items[self.first_item_to_show + 2][0]
					self.textbox_5v.text = self._get_param(self.menu_items[self.first_item_to_show + 2][1])
				else:
					self.textbox_5.text = ""
					self.textbox_5v.text = ""

			# and finally, adjust the red highlight to put it on current item
			if ((self.first_item_to_show + 0) == self.currently_selected_list_item):
				self.textbox_3.color = mycolors.WHITE
				self.textbox_3v.color = mycolors.GREEN

			if ((self.first_item_to_show + 1) == self.currently_selected_list_item):
				self.textbox_4.color = mycolors.WHITE
				self.textbox_4v.color = mycolors.GREEN

			if ((self.first_item_to_show + 2) == self.currently_selected_list_item):
				self.textbox_5.color = mycolors.WHITE
				self.textbox_5v.color = mycolors.GREEN

			time.sleep(0.1)

	def _scroll_param(self, param, updown):
		if (param == "THR"):
			temp = self.mode_followpath.scroll_following_throttle(updown)
		elif (param == "LPS"):
			temp = self.mode_followpath.scroll_following_loop_speed(updown)
		elif (param == "RR"):
			temp = self.mode_followpath.scroll_following_rxn_rate(updown)
		else:
			temp = 0
		return temp

	def _get_param(self, param):
		if (param == "THR"):
			temp = self.mode_followpath.get_following_throttle()
		elif (param == "LPS"):
			temp = self.mode_followpath.get_following_loop_speed()
		elif (param == "RR"):
			temp = self.mode_followpath.get_following_rxn_rate()
		else:
			temp = 0
		return temp
