"""
# Controller for Line-Following Robot
# This runs on an Adafruit Feather M4, with a MiniTFT board.  
# It drives a TB6612 to control 2 DC Motors (in blue servo case)
# and talks over I2C to an ItsyBitsy that interfaces a Pololu 
# line following sensor
#
# Author(s): Don Korte
# Module:  screen_dashboard.py generates and manages framework to display 
#	runtime dashboard that shows line sensor position, throttle, and 
#	various statistics
#
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
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.triangle import Triangle

import mycolors

BALL_DIAMETER = 18
BALL_RADIUS = 9
LINE_POS_BOX_HEIGHT = BALL_DIAMETER + 2
THROT_BOX_WIDTH = 16
GUTTER = 8	# gap between thottle boxes and line position box


class Screen_Dashboard:
	def __init__(self, tft_device, mode_config):
		self.this_tft = tft_device
		self.mode_config = mode_config
		self.screen_width = self.this_tft.display.width
		self.screen_height = self.this_tft.display.height

		self.this_group = displayio.Group(max_size=16) 

		# write instructions at bottom of screen
		self.textbox_1 = label.Label(terminalio.FONT, text= "", max_glyphs=36, color=mycolors.YELLOW, x=0, y=self.screen_height-28)
		self.this_group.append(self.textbox_1)

		# write instructions at bottom of screen
		self.textbox_2 = label.Label(terminalio.FONT, text= "", max_glyphs=36, color=mycolors.YELLOW, x=0, y=self.screen_height-14)
		self.this_group.append(self.textbox_2)

		# doublesize text box for duration or countdown
		self.textbox_3 = label.Label(terminalio.FONT, text= "", max_glyphs=18, color=mycolors.YELLOW, x=0, y=(LINE_POS_BOX_HEIGHT + 2), scale=2)
		self.this_group.append(self.textbox_3)

		# this box overlaps double-size box 3 but is single size; first single-size row
		self.textbox_4 = label.Label(terminalio.FONT, text= "", max_glyphs=36, color=mycolors.YELLOW, x=0, y=(LINE_POS_BOX_HEIGHT + 2))
		self.this_group.append(self.textbox_4)

		# this box overlaps double-size box 3 but is single size; second single-size row
		self.textbox_5 = label.Label(terminalio.FONT, text= "", max_glyphs=36, color=mycolors.YELLOW, x=0, y=(LINE_POS_BOX_HEIGHT + 2 + 14))
		self.this_group.append(self.textbox_5)

		# create white rectangle at top to serve as gage backgroundfield for line sensor ball
		self.lineposition_box = Rect((THROT_BOX_WIDTH + GUTTER), 0, 
			self.screen_width-(2 * (THROT_BOX_WIDTH + GUTTER)), LINE_POS_BOX_HEIGHT, 
			fill=mycolors.WHITE, outline=mycolors.WHITE)
		self.this_group.append(self.lineposition_box)

		initial_x = int(self.screen_width/2)
		self.lineposition_marker = Circle(initial_x, BALL_RADIUS+1, BALL_RADIUS, 
			fill=mycolors.PASTEL_GREEN, outline=None)
		self.this_group.append(self.lineposition_marker)

		self.centerline = Line(int(self.screen_width/2), 0, int(self.screen_width/2), LINE_POS_BOX_HEIGHT, mycolors.DARK_GRAY)
		self.this_group.append(self.centerline)

		# create left and right throttle display gage boxes 
		self.left_throtgage_box = Rect(0, 0, 
			THROT_BOX_WIDTH, self.screen_height, 
			fill=mycolors.LIGHT_GRAY, outline=mycolors.LIGHT_GRAY)
		self.this_group.append(self.left_throtgage_box)

		self.right_throtgage_box = Rect(self.screen_width-THROT_BOX_WIDTH, 0, 
			THROT_BOX_WIDTH, self.screen_height, 
			fill=mycolors.LIGHT_GRAY, outline=mycolors.LIGHT_GRAY)
		self.this_group.append(self.right_throtgage_box)

		# and corresponding left and right throttle value (initially "unfilled")
		self.left_throtval_box = Rect(1, 0, 
			(THROT_BOX_WIDTH - 2), self.screen_height, 
			fill=mycolors.DARK_GRAY, outline=mycolors.DARK_GRAY)
		self.this_group.append(self.left_throtval_box)

		self.right_throtval_box = Rect(self.screen_width-(THROT_BOX_WIDTH - 1), 0, 
			(THROT_BOX_WIDTH - 2), self.screen_height, 
			fill=mycolors.DARK_GRAY, outline=mycolors.DARK_GRAY)
		self.this_group.append(self.right_throtval_box)


	def show_this_screen(self):
		self.this_tft.display.show(self.this_group)

	# displays rectangle in left throttle gage block representing throttle value
	# at entry throtval is -1 through +1
	# displayed bar is green if positive throttle (forwards), red if negative (backwards)
	def show_left_throttle(self, throtval=0):
		if (self.mode_config.get_showdisp() == "Yes"):
			self.left_throtval_box.y = 0
			self.left_throtval_box.height = self.screen_height
			self.left_throtval_box.fill = mycolors.DARK_GRAY

			throt_pixels_tall = abs(int(throtval * self.screen_height))
			self.left_throtval_box.y = self.screen_height - throt_pixels_tall
			self.left_throtval_box.height = throt_pixels_tall
			if (throtval >= 0):
				self.left_throtval_box.fill = mycolors.GREEN
			else:
				self.left_throtval_box.fill = mycolors.RED

	# displays rectangle in right throttle gage block representing throttle value
	# at entry throtval is -1 through +1
	# displayed bar is green if positive throttle (forwards), red if negative (backwards)
	def show_right_throttle(self, throtval=0):
		if (self.mode_config.get_showdisp() == "Yes"):
			self.right_throtval_box.y = 0
			self.right_throtval_box.height = self.screen_height
			self.right_throtval_box.fill = mycolors.DARK_GRAY

			throt_pixels_tall = abs(int(throtval * self.screen_height))
			self.right_throtval_box.y = self.screen_height - throt_pixels_tall
			self.right_throtval_box.height = throt_pixels_tall
			if (throtval >= 0):
				self.right_throtval_box.fill = mycolors.GREEN
			else:
				self.right_throtval_box.fill = mycolors.RED

	# displays bal representing line position
	# at entry line_position is 0-250 with 125=center
	# displayed ball is green if abs(line_position-125) < 30; 	
	# displayed ball is orange if abs(line_position-125) < 90; 
	# ortherwise blue
	# 
	def show_line_position(self, line_position=125):
		if (self.mode_config.get_showdisp() == "Yes"):
			gage_box_width = self.screen_width - ( 2* (THROT_BOX_WIDTH + GUTTER))
			half_width = (gage_box_width - BALL_RADIUS) / 2
			pixels_per_count = half_width / 125		

			self.lineposition_marker.x = int(self.screen_width/2) + int(pixels_per_count * (line_position - 125)) - BALL_RADIUS
			
			if (abs(line_position - 125) < 30):
				current_color = mycolors.GREEN
			elif (abs(line_position - 125) < 90):
				current_color = mycolors.ORANGE
			else:
				current_color = mycolors.BLUE

			self.lineposition_marker.fill = current_color

	# this function hides the line position marker by turning it the same color as its background
	def hide_line_position(self):
		self.lineposition_marker.fill = mycolors.WHITE


	def set_text1(self, text, color=mycolors.YELLOW, justify="C"):
		self.textbox_1.color = color
		self.textbox_1.text = text
		if (justify == "L"):
			self.textbox_1.x = THROT_BOX_WIDTH + GUTTER
		elif (justify == "R"):
			_, _, textwidth, _ = self.textbox_1.bounding_box
			self.textbox_1.x = self.screen_width - textwidth - (THROT_BOX_WIDTH + GUTTER)
		else:
			_, _, textwidth, _ = self.textbox_1.bounding_box
			self.textbox_1.x = int(self.screen_width/2) - int(textwidth/2)


	def set_text2(self, text, color=mycolors.YELLOW, justify="C"):
		self.textbox_2.color = color
		self.textbox_2.text = text
		if (justify == "L"):
			self.textbox_2.x = THROT_BOX_WIDTH + GUTTER
		elif (justify == "R"):
			_, _, textwidth, _ = self.textbox_2.bounding_box
			self.textbox_2.x = self.screen_width - textwidth - (THROT_BOX_WIDTH + GUTTER)
		else:
			_, _, textwidth, _ = self.textbox_2.bounding_box
			self.textbox_2.x = int(self.screen_width/2) - int(textwidth/2)

	def set_text3(self, text, color=mycolors.YELLOW, justify="C"):
		self.textbox_3.color = color
		self.textbox_3.text = text
		_, _, textwidth, _ = self.textbox_3.bounding_box
		if (justify == "L"):
			self.textbox_3.x = THROT_BOX_WIDTH + GUTTER
		elif (justify == "R"):
			# note here we don't divide textwidth by 2 because the font is scaled up by 2 (so  (width/2) * 2 )
			_, _, textwidth, _ = self.textbox_3.bounding_box
			self.textbox_3.x = self.screen_width - (THROT_BOX_WIDTH + GUTTER) - (textwidth * 2)
		else:
			# note here we don't divide textwidth by 2 because the font is scaled up by 2 (so  (width/2) * 2 )
			self.textbox_3.x = int(self.screen_width/2) - textwidth

	# note this overlaps box 3 
	def set_text4(self, text, color=mycolors.YELLOW, justify="C"):
		self.textbox_4.color = color
		self.textbox_4.text = text
		if (justify == "L"):
			self.textbox_4.x = THROT_BOX_WIDTH + GUTTER
		elif (justify == "R"):
			_, _, textwidth, _ = self.textbox_4.bounding_box
			self.textbox_4.x = self.screen_width - textwidth - (THROT_BOX_WIDTH + GUTTER)
		else:
			_, _, textwidth, _ = self.textbox_4.bounding_box
			self.textbox_4.x = int(self.screen_width/2) - int(textwidth/2)

	# note this overlaps box 3 
	def set_text5(self, text, color=mycolors.YELLOW, justify="C"):
		self.textbox_5.color = color
		self.textbox_5.text = text
		if (justify == "L"):
			self.textbox_5.x = THROT_BOX_WIDTH + GUTTER
		elif (justify == "R"):
			_, _, textwidth, _ = self.textbox_5.bounding_box
			self.textbox_5.x = self.screen_width - textwidth - (THROT_BOX_WIDTH + GUTTER)
		else:
			_, _, textwidth, _ = self.textbox_5.bounding_box
			self.textbox_5.x = int(self.screen_width/2) - int(textwidth/2)
