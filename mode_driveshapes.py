"""
# Controller for Line-Following Robot
# This runs on an Adafruit Feather M4, with a MiniTFT board.  
# It drives a TB6612 to control 2 DC Motors (in blue servo case)
# and talks over I2C to an ItsyBitsy that interfaces a Pololu 
# line following sensor
#
# Author(s): Don Korte
# Module:  mode_driveshapes.py has functions that drive simple
#	shapes and lines for testing and motor calibration purposes
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

import time
import mycolors


class Mode_DriveShapes:
	def __init__(self, screen_dashboard, device_motors, device_linesense, device_storage):
		self.screen_dashboard = screen_dashboard
		self.device_motors = device_motors
		self.device_linesense = device_linesense
		self.device_storage = device_storage
		self.lineposition = 0	# initially say its in middle (-125 to +125)
		self.throttle_left = 0	# -100 full back, +100=full fwd, 0=stopped
		self.throttle_right = 0	# -100 full back, +100=full fwd, 0=stopped


	# this function initiates mode, runs it till done, then returns text string indicating next mode
	def run_straight(self):
		self.screen_dashboard.show_this_screen()
		status = self.prepare_to_start()
		if (status == "CANCEL"):
			return "MAINMENU"
		self.screen_dashboard.set_text1("Driving Straight 100 cm")		
		self.screen_dashboard.set_text2("Click A to quit")	
		self.screen_dashboard.set_text3("", mycolors.PINK, "C")	
		self.screen_dashboard.set_text4("")	
		self.screen_dashboard.set_text5("")	

		self.device_motors.motors_accelerate(0.6)
		self.device_motors.move_forward(0.6)
		time.sleep(100/30)		
		self.device_motors.motors_accelerate(0)
		self.device_motors.motors_stop()
		return "MAINMENU"

		
	def run_curveleft(self):
		self.screen_dashboard.show_this_screen()
		status = self.prepare_to_start()
		if (status == "CANCEL"):
			return "MAINMENU"
		self.screen_dashboard.set_text1("Curving Left")		
		self.screen_dashboard.set_text2("Click A to quit")	
		self.screen_dashboard.set_text3("", mycolors.PINK, "C")	
		self.screen_dashboard.set_text4("")	
		self.screen_dashboard.set_text5("")	

		self.device_motors.motors_accelerate(0.5)
		self.device_motors.move_forward_curved(0.5, -0.2)
		time.sleep(2)	
		self.device_motors.motors_accelerate(0)
		self.device_motors.motors_stop()
		return "MAINMENU"

	def run_curveright(self):
		self.screen_dashboard.show_this_screen()
		status = self.prepare_to_start()
		if (status == "CANCEL"):
			return "MAINMENU"
		self.screen_dashboard.set_text1("Curving Right")		
		self.screen_dashboard.set_text2("Click A to quit")	
		self.screen_dashboard.set_text3("", mycolors.PINK, "C")	
		self.screen_dashboard.set_text4("")	
		self.screen_dashboard.set_text5("")	

		self.device_motors.motors_accelerate(0.5)
		self.device_motors.move_forward_curved(0.5, 0.1)
		time.sleep(2)	
		self.device_motors.motors_accelerate(0)
		self.device_motors.motors_stop()
		return "MAINMENU"

	def follow_path(self):
		# fake_location = 0
		# fake_increment = 5

		while True:
		    buttons = self.screen_dashboard.this_tft.buttons

		    if buttons.a:
		        # print("Button A cycle")
		        still_pressed = True
		        while  still_pressed:
		        	buttons = self.screen_dashboard.this_tft.buttons
		        	still_pressed = buttons.a
		        	time.sleep(0.05)
		        # print("released")
		        return 

		    # fake_location += fake_increment

		    # if (fake_location > 90):
		    # 	fake_increment = -5
		    # if (fake_location < -90):
		    # 	fake_increment = 5

		    # fake_location = 100
		    self.lineposition = self.device_linesense.get_position() - 125
		    print("current line position:", self.lineposition)
		    self.screen_dashboard.show_line_position(self.lineposition)

		    fake_throttle =int(self.lineposition * 0.8)
		    self.screen_dashboard.show_left_throttle(fake_throttle)
		    self.screen_dashboard.show_right_throttle(fake_throttle)

		    time.sleep(0.3) 

	def prepare_to_start(self):
		self.screen_dashboard.show_left_throttle(0)
		self.screen_dashboard.show_right_throttle(0)
		# self.screen_dashboard.hide_line_position()

		self.screen_dashboard.set_text1("Place robot on track")		
		self.screen_dashboard.set_text2("with sensor over line")	
		self.screen_dashboard.set_text4("Run # 1", mycolors.WHITE, "L")
		self.screen_dashboard.set_text5("Starting Soon", mycolors.WHITE, "L")

		time_til_start = 5
		while(time_til_start > 0):
			self.screen_dashboard.set_text3("    "+str(time_til_start), mycolors.PINK, "R")
			time_til_start -= 1
			# now wait 1 second, but check for "A" button cancel every 0.1 seconds
			for i in range(10):	
				buttons = self.screen_dashboard.this_tft.buttons
				if buttons.a:
				    still_pressed = True
				    while  still_pressed:
				    	buttons = self.screen_dashboard.this_tft.buttons
				    	still_pressed = buttons.a
				    	time.sleep(0.05)
				    # print("released")
				    return "CANCEL"
				time.sleep(0.1)

		self.screen_dashboard.set_text4("")		# clear out run number
		self.screen_dashboard.set_text5("")		# clear out "starting soon"
		return "READY"

