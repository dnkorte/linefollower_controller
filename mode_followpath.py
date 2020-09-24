"""
# Controller for Line-Following Robot
# This runs on an Adafruit Feather M4, with a MiniTFT board.  
# It drives a TB6612 to control 2 DC Motors (in blue servo case)
# and talks over I2C to an ItsyBitsy that interfaces a Pololu 
# line following sensor
#
# Author(s): Don Korte
# Module:  mode_followpath.py has the code that controls the actual
#	path-following driving algorithm
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


class Mode_FollowPath:
	def __init__(self, screen_dashboard, device_motors, device_linesense, device_storage):
		self.screen_dashboard = screen_dashboard
		self.device_motors = device_motors
		self.device_linesense = device_linesense
		self.device_storage = device_storage
		self.lineposition = 0	# initially say its in middle (-125 to +125)
		self.throttle_left = 0	# -100 full back, +100=full fwd, 0=stopped
		self.throttle_right = 0	# -100 full back, +100=full fwd, 0=stopped
		self.run_number = 0		# run number since powerup
		self.num_green = 0		# number of cycles in green range
		self.num_left = 0		# number of cycles left of center (left of "green" range)
		self.num_right = 0		# number of cycles right of center (right of "green" range)
		self.num_offtrack = 0	# number of cycles totally off the track (either direction)
		self.num_loops = 0		# total number of cycles (loops) on this run
		self.total_calc_time = 0	# total seconds in all loops (calc time not including loopdelay)

		# initial testing suggests 0.4 throttle, 0.02 or 0.01 loop speed, 1.3 rxn rate
		# 1.4 rxn rate is just a little bit too fast -- it overcorrects
		self.throttle_options = [ 0.2, 0.3, 0.4, 0.5, 0.6, 0.7 ]
		self.throttle_index = 2
		self.loop_speed_options = [ 0.01, 0.02, 0.03, 0.04, 0.05, 0.1, 0.15, 0.2 ]
		self.loop_speed_index = 1
		self.rxn_rate_options = [ 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.3, 1.4] 
		self.rxn_rate_index = 7

		# following equation coefficients (default values)
		self.following_throttle = self.throttle_options[self.throttle_index]
		self.following_loop_speed = self.loop_speed_options[self.loop_speed_index]
		self.following_rxn_rate = self.rxn_rate_options[self.rxn_rate_index]	# 1=super fast rxns; 0.2 = really sluggish


	# this function initiates mode, runs it till done, then returns text string indicating next mode
	def run_mode(self):
		self.screen_dashboard.show_this_screen()
		self.run_number += 1
		status = self.prepare_to_start()
		if (status == "CANCEL"):
			return "MAINMENU"
		self.screen_dashboard.set_text1("", mycolors.RED, "C")		
		self.screen_dashboard.set_text2("Click A to quit")	
		self.screen_dashboard.set_text3("", mycolors.PINK, "C")	
		self.screen_dashboard.set_text4("")	
		self.screen_dashboard.set_text5("")	

		self.num_green = 0		# number of cycles in green range
		self.num_left = 0		# number of cycles left of center (left of "green" range)
		self.num_right = 0		# number of cycles right of center (right of "green" range)
		self.num_offtrack = 0	# number of cycles totally off the track (either direction)
		self.num_loops = 0		# total number of cycles (loops) on this run
		self.total_calc_time = 0	# total seconds in all loops (not including loop_delay)

		self.device_motors.motors_accelerate(self.following_throttle)
		while True:
			start_time = time.monotonic()
			buttons = self.screen_dashboard.this_tft.buttons

			if buttons.a:
			    # print("Button A cycle")
			    still_pressed = True
			    while  still_pressed:
			    	buttons = self.screen_dashboard.this_tft.buttons
			    	still_pressed = buttons.a
			    	time.sleep(0.05)
			    # print("released")
			    self.device_motors.motors_accelerate(0)
			    return 


			self.lineposition = self.device_linesense.get_position()
			self.screen_dashboard.show_line_position(self.lineposition)

			curve = -1 * (self.lineposition - 125) / (125 / self.following_rxn_rate)
			self.device_motors.move_forward_curved(self.following_throttle, curve)
			# print("current line position:", self.lineposition, " curve:", curve)

			# note that little numbers mean i'm LEFT of line (line is to my right)
			# big numbers mean i'm RIGHT of line (line is to my left)
			# numbers < 5 or > 245 are basically OFF the line
			if (abs(self.lineposition - 125) < 30):
				self.num_green += 1
			if ((self.lineposition < 5) or (self.lineposition > 245)):
				self.num_offtrack += 1
			if (self.lineposition < 95):
				self.num_left += 1
			if (self.lineposition > 155):
				self.num_right += 1
			self.num_loops += 1

			#pct_on_track = int(100 * (self.num_loops - self.num_offtrack) / self.num_loops)
			#if (pct_on_track > 85):
			#	temp = mycolors.GREEN
			#elif (pct_on_track > 50):
			#	temp = mycolors.YELLOW
			#else:
			#	temp = mycolors.RED
			# print(self.num_loops, self.num_offtrack, pct_on_track)
			#self.screen_dashboard.set_text3(str(pct_on_track), temp, "C")

			# temp = "L:" + str(self.num_left) + "   R:" + str(self.num_left)
			# self.screen_dashboard.set_text1(temp, mycolors.RED, "C")

			end_time = time.monotonic()		# typically about 0.021 sec (0.016 if no "pct_on_track" disp)
			self.total_calc_time += (end_time - start_time)
			print(end_time - start_time)
			time.sleep(self.following_loop_speed) 

		# add a run summary screen here... (and eventually SD card storage)
		return "MAINMENU"


	def prepare_to_start(self):
		self.screen_dashboard.show_left_throttle(0)
		self.screen_dashboard.show_right_throttle(0)
		# self.screen_dashboard.hide_line_position()

		self.screen_dashboard.set_text1("Place robot on track")		
		self.screen_dashboard.set_text2("with sensor over line")
		temp = "Run # " + str(self.run_number)	
		self.screen_dashboard.set_text4(temp, mycolors.WHITE, "L")
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

	def get_following_throttle(self):
		return self.following_throttle

	# updown determines direction : (-) scrolls down, (+) scrolls up
	def scroll_following_throttle(self, updown):
		if (updown < 0):
			self.throttle_index -= 1
			if (self.throttle_index < 0):
				self.throttle_index = len(self.throttle_options) - 1
		else:
			self.throttle_index += 1
			if (self.throttle_index > (len(self.throttle_options) - 1)):
				self.throttle_index = 0
		self.following_throttle = self.throttle_options[self.throttle_index]
		return self.following_throttle



	def get_following_loop_speed(self):
		return self.following_loop_speed

	# updown determines direction : (-) scrolls down, (+) scrolls up
	def scroll_following_loop_speed(self, updown):
		if (updown < 0):
			self.loop_speed_index -= 1
			if (self.loop_speed_index < 0):
				self.loop_speed_index = len(self.loop_speed_options) - 1
		else:
			self.loop_speed_index += 1
			if (self.loop_speed_index > (len(self.loop_speed_options) - 1)):
				self.loop_speed_index = 0
		self.following_loop_speed = self.loop_speed_options[self.loop_speed_index]
		return self.following_loop_speed


	def get_following_rxn_rate(self):
		return self.following_rxn_rate

	# updown determines direction : (-) scrolls down, (+) scrolls up
	def scroll_following_rxn_rate(self, updown):
		if (updown < 0):
			self.rxn_rate_index -= 1
			if (self.rxn_rate_index < 0):
				self.rxn_rate_index = len(self.rxn_rate_options) - 1
		else:
			self.rxn_rate_index += 1
			if (self.rxn_rate_index > (len(self.rxn_rate_options) - 1)):
				self.rxn_rate_index = 0
		self.following_rxn_rate = self.rxn_rate_options[self.rxn_rate_index]
		return self.following_rxn_rate