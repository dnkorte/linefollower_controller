"""
# Controller for Line-Following Robot
# This runs on an Adafruit Feather M4, with a MiniTFT board.  
# It drives a TB6612 to control 2 DC Motors (in blue servo case)
# and talks over I2C to an ItsyBitsy that interfaces a Pololu 
# line following sensor
#
# Author(s): Don Korte
# Module:  device_motors.py manages motor drive for 2 DC motors
#
# github: https://github.com/dnkorte/linefollower_controller
##
# note that dc motors in mg90 cases turn approx 120 rpm at 100% pwm
#    120 rpm = 2 rev/sec.   for 2in wheel this is 12 in / sec
#    for 80mm minirobot, wheels are on 2 in radius from axis of rotation
#	 so a 360 degree turn is 12 in of circumference or 1 second
#    a 90 degree turn is approx 0.25 sec.  Note also that these motors
#    are basically too fast for this application -- they need to run at 
#    40% throttle or less for reasonable speeds -- and 20% (or thereabouts
#    is the very bottom end for these motors -- they have no torque or 
#    reliability at this speed)
# 
# Note (dnk) with a 6v Vmot, 0.20 throttle is about the slowest they can go
#    
# reference adafruit motor library guide: 
#	https://circuitpython.readthedocs.io/projects/motor/en/latest/api.html
# 	The TB6612 boards feature three inputs XIN1, XIN2 and PWMX. Since we 
# 	PWM the INs directly its expected that the PWM pin is consistently high.
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
import pulseio
import board
import math
from digitalio import DigitalInOut, Direction
from adafruit_motor import motor

# ------------------------------------------------------------------

class Device_Motors:
	def __init__(self, screen_dashboard):
		self.screen_dashboard = screen_dashboard
		self.max_accel = 10		# max allowed acceleration in pct per 0.1 sec
		self.current_throt_left = 0
		self.current_throt_right = 0

		self.Ain1 = pulseio.PWMOut(board.D10, frequency=1600)
		self.Ain2 = pulseio.PWMOut(board.D9, frequency=1600)
		self.motorR = motor.DCMotor(self.Ain1, self.Ain2)
		self.Bin1 = pulseio.PWMOut(board.D11, frequency=1600)
		self.Bin2 = pulseio.PWMOut(board.D12, frequency=1600)
		self.motorL = motor.DCMotor(self.Bin1, self.Bin2)
		# 
		# speed calibration constants to equalize motor speed
		# note each throttle request is multiplied by this per-motor constant
		# the "slower" motor should be set to 1.0, 
		# the faster motor should be set to whatever it takes to reduces its speed
		# to match slower motor
		# 
		self.motorCalibrateL = 1
		self.motorCalibrateR = 0.95

		self.motorCalibrateL_turn = 0.80
		self.motorCalibrateR_turn = 1

		# throttle and duration for 90 (or 180) degree turn-in-place
		# assumes one motor goes forward, the other back at same throttle
		self.seconds_for_360 = SECONDS_FOR_360 = 2.5
		self.throttle_for_360 = 0.25 

		self.cm_per_sec_at_100pct = 60
		self.cm_per_sec_at_25pct = 15

		self.max_delta_throt_per_100ms = 0.1

#
# ##############################################################################
# for motion commands, throttle values are -1.0 (back) => 0 => 1.0 (forward)
# ##############################################################################
# 

	def move_forward(self, targetThrottle):
		self.current_throt_left = targetThrottle
		self.current_throt_right = targetThrottle
		self.motorL.throttle = self.current_throt_left * self.motorCalibrateL
		self.motorR.throttle = self.current_throt_right * self.motorCalibrateR
		self.screen_dashboard.show_left_throttle(self.current_throt_left)
		self.screen_dashboard.show_right_throttle(self.current_throt_right)

	def move_backward(self, targetThrottle):
		self.current_throt_left = targetThrottle * (-1)
		self.current_throt_right = targetThrottle * (-1)
		self.motorL.throttle = self.current_throt_left * self.motorCalibrateL
		self.motorR.throttle = self.current_throt_right * self.motorCalibrateR
		self.screen_dashboard.show_left_throttle(self.current_throt_left)
		self.screen_dashboard.show_right_throttle(self.current_throt_right)

#
# function move_forward_curved() is like move_forward except that it introduces
# a bias to curve the direction to left or right.  the "curve" parameter has
# a value from -1.0 => 0 => 1.0 where 0 has no effect (goes straight), 
# and negative numbers make the curve bend to the left, positive numbers
# make it bend to the right 
# 
# note that for my motors, 0.1 makes a nice gentle curve to the right
# that is matched by a -0.2 which gently curves to the left
# 
	def move_forward_curved(self, targetThrottle, curve):
		self.current_throt_left = targetThrottle + (targetThrottle*curve/2)
		if (self.current_throt_left < 0):
			self.current_throt_left = 0
		if (self.current_throt_left > 1):
			self.current_throt_left = 1
		self.current_throt_right = targetThrottle - (targetThrottle*curve/2)
		if (self.current_throt_right < 0):
			self.current_throt_right = 0
		if (self.current_throt_right > 1):
			self.current_throt_right = 1
		self.motorL.throttle = self.current_throt_left * self.motorCalibrateL
		self.motorR.throttle = self.current_throt_right * self.motorCalibrateR
		self.screen_dashboard.show_left_throttle(self.current_throt_left)
		self.screen_dashboard.show_right_throttle(self.current_throt_right)

#
# function motors_accelerate() is like move forward accept that instead of
# immediately setting throttle to the targetThrottle it honors a "max acceleration rate"
# configuration parameter and steps gradually to the targetThrottle.  it returns
# the number of seconds that it took to get there.
# 
	def motors_accelerate(self, targetThrottle):
		if (abs(abs(targetThrottle) - abs(self.current_throt_left)) < self.max_delta_throt_per_100ms):
			# new throttle is close to current to can just go there
			#pass
			print("already close enough - just going to:", targetThrottle)
		elif (targetThrottle < self.current_throt_left):
			# will have to go in steps, and they will be steps DOWN
			while ((self.current_throt_left - targetThrottle) > self.max_delta_throt_per_100ms):
				self.current_throt_left = self.current_throt_left - self.max_delta_throt_per_100ms
				self.current_throt_right = self.current_throt_right - self.max_delta_throt_per_100ms
				self.motorL.throttle = self.current_throt_left * self.motorCalibrateL
				self.motorR.throttle = self.current_throt_right * self.motorCalibrateR
				self.screen_dashboard.show_left_throttle(self.current_throt_left)
				self.screen_dashboard.show_right_throttle(self.current_throt_right)
				print("stepping up:", self.current_throt_left)
				time.sleep(0.1)
		else:
			# will have to go in steps, and the will be steps UP
			while ((targetThrottle - self.current_throt_left) > self.max_delta_throt_per_100ms):
				self.current_throt_left = self.current_throt_left + self.max_delta_throt_per_100ms
				self.current_throt_right = self.current_throt_right + self.max_delta_throt_per_100ms
				self.motorL.throttle = self.current_throt_left * self.motorCalibrateL
				self.motorR.throttle = self.current_throt_right * self.motorCalibrateR
				self.screen_dashboard.show_left_throttle(self.current_throt_left)
				self.screen_dashboard.show_right_throttle(self.current_throt_right)
				print("stepping down:", self.current_throt_left)
				time.sleep(0.1)

		self.current_throt_left = targetThrottle
		self.current_throt_right = targetThrottle
		self.motorL.throttle = self.current_throt_left * self.motorCalibrateL
		self.motorR.throttle = self.current_throt_right * self.motorCalibrateR
		self.screen_dashboard.show_left_throttle(self.current_throt_left)
		self.screen_dashboard.show_right_throttle(self.current_throt_right)
#
# function turn_in_place() spins the robot "in place" (without forward movement)
# degrees is amount to turn, in degrees (-) is left, (+) is right
#


	def turn_in_place(self, degrees):
		self.current_throt_left = math.copysign(self.throttle_for_360, degrees)
		self.current_throt_right = math.copysign(self.throttle_for_360, degrees) * (-1)
		self.motorL.throttle = self.current_throt_left * self.motorCalibrateL_turn
		self.motorR.throttle = self.current_throt_right * self.motorCalibrateR_turn
		#self.motorL.throttle = self.current_throt_left 
		#self.motorR.throttle = self.current_throt_right 
		self.screen_dashboard.show_left_throttle(self.current_throt_left)
		self.screen_dashboard.show_right_throttle(self.current_throt_right)

		duration = abs(degrees * self.seconds_for_360) / 360
		time.sleep(duration)

		self.motors_stop()

#
# function motors_stop() causes both motors to stop turning immediately
# no deceleration curve is applied
# 
	def motors_stop(self):
		self.current_throt_left = 0
		self.current_throt_right = 0
		self.motorL.throttle = self.current_throt_left * self.motorCalibrateL
		self.motorR.throttle = self.current_throt_right * self.motorCalibrateR
		self.screen_dashboard.show_left_throttle(self.current_throt_left)
		self.screen_dashboard.show_right_throttle(self.current_throt_right)



"""
		self.motorR.throttle = 0.20 * myconfig.MOTOR_CALIBRATE_R
		self.motorL.throttle = 0.20 * myconfig.MOTOR_CALIBRATE_L
		time.sleep(0.2)
		self.motorR.throttle = 0.30 * myconfig.MOTOR_CALIBRATE_R
		self.motorL.throttle = 0.30 * myconfig.MOTOR_CALIBRATE_L
		time.sleep(0.2)
		self.motorR.throttle = 0.40 * myconfig.MOTOR_CALIBRATE_R
		self.motorL.throttle = 0.40 * myconfig.MOTOR_CALIBRATE_L
		time.sleep(0.1)
		#self.motorR.throttle = 0.50 * myconfig.MOTOR_CALIBRATE_R
		#self.motorL.throttle = 0.50 * myconfig.MOTOR_CALIBRATE_L
		#time.sleep(0.1)
		#self.motorR.throttle = 0.60 * myconfig.MOTOR_CALIBRATE_R
		#self.motorL.throttle = 0.60 * myconfig.MOTOR_CALIBRATE_L
		#time.sleep(0.1)
		#self.motorR.throttle = 0.70 * myconfig.MOTOR_CALIBRATE_R
		#self.motorL.throttle = 0.70 * myconfig.MOTOR_CALIBRATE_L
		#time.sleep(0.1)
		self.motorR.throttle = 0.80 * myconfig.MOTOR_CALIBRATE_R
		self.motorL.throttle = 0.80 * myconfig.MOTOR_CALIBRATE_L
		time.sleep(3)
		self.motorR.throttle = 0.50 * myconfig.MOTOR_CALIBRATE_R
		self.motorL.throttle = 0.50 * myconfig.MOTOR_CALIBRATE_L
		time.sleep(0.2)
		self.motorR.throttle = 0.25 * myconfig.MOTOR_CALIBRATE_R
		self.motorL.throttle = 0.25 * myconfig.MOTOR_CALIBRATE_L
		time.sleep(0.2)
		self.motorR.throttle = 0
		self.motorL.throttle = 0
		return

		self.motorR.throttle = myconfig.THROTTLE_FOR_90_TIP * myconfig.MOTOR_CALIBRATE_R
		self.motorL.throttle = myconfig.THROTTLE_FOR_90_TIP * myconfig.MOTOR_CALIBRATE_L * (-1)
		time.sleep(myconfig.SECONDS_FOR_90_TIP)
		self.motorR.throttle = myconfig.THROTTLE_FOR_180_TIP * myconfig.MOTOR_CALIBRATE_R * (-1)
		self.motorL.throttle = myconfig.THROTTLE_FOR_180_TIP * myconfig.MOTOR_CALIBRATE_L
		time.sleep(myconfig.SECONDS_FOR_180_TIP)
		self.motorR.throttle = myconfig.THROTTLE_FOR_180_TIP * myconfig.MOTOR_CALIBRATE_R 
		self.motorL.throttle = myconfig.THROTTLE_FOR_180_TIP * myconfig.MOTOR_CALIBRATE_L * (-1)
		time.sleep(myconfig.SECONDS_FOR_180_TIP)
		self.motorR.throttle = myconfig.THROTTLE_FOR_90_TIP * myconfig.MOTOR_CALIBRATE_R * (-1)
		self.motorL.throttle = myconfig.THROTTLE_FOR_90_TIP * myconfig.MOTOR_CALIBRATE_L
		time.sleep(myconfig.SECONDS_FOR_90_TIP)
		self.motorR.throttle = 0.25
		self.motorL.throttle = 0.25
		time.sleep(1)
		self.motorR.throttle = 0
		self.motorL.throttle = 0
"""

"""
	# 
	# for these simple functions, throttle ranges -1.0 to +1.0
	#
	
	def move_forward(self, targetThrottle, duration):
		self.motorL.throttle = targetThrottle * self.motorCalibrateL
		self.motorR.throttle = targetThrottle * self.motorCalibrateR
		self.screen_dashboard.show_left_throttle(self.motorL.throttle*100)
		self.screen_dashboard.show_right_throttle(self.motorR.throttle*100)
		time.sleep(duration)

	def move_backward(self, targetThrottle, duration):
		self.motorL.throttle = -1 * targetThrottle * self.motorCalibrateL
		self.motorR.throttle = -1 * targetThrottle * self.motorCalibrateR
		self.screen_dashboard.show_left_throttle(self.motorL.throttle*100)
		self.screen_dashboard.show_right_throttle(self.motorR.throttle*100)
		time.sleep(duration)
	    
	def turn_R_90(self):
		targetThrottle = 0.6
		self.motorL.throttle = targetThrottle * self.motorCalibrateL
		self.motorR.throttle = 0
		self.screen_dashboard.show_left_throttle(self.motorL.throttle*100)
		self.screen_dashboard.show_right_throttle(self.motorR.throttle*100)
		time.sleep(0.72)
	   
	def turn_L_90(self):
		targetThrottle = 0.6
		self.motorL.throttle = 0
		self.motorR.throttle = targetThrottle * self.motorCalibrateR
		self.screen_dashboard.show_left_throttle(self.motorL.throttle*100)
		self.screen_dashboard.show_right_throttle(self.motorR.throttle*100)
		time.sleep(0.72)
	    
	def motors_stop(self):
		self.motorL.throttle = 0
		self.motorR.throttle = 0
		self.screen_dashboard.show_left_throttle(self.motorL.throttle*100)
		self.screen_dashboard.show_right_throttle(self.motorR.throttle*100)
"""

"""
# --------------------------------------------------------------------------------------
	# set throttle -100 (back) => 0 => +100 (fwd)
	def set_left_throttle(self, newthrottle):
		self.target_throt_left = newthrottle
		self.delta_throt_left = abs((newthrottle - self.current_throt_left) / 10)
		if (self.delta_throt_left > self.max_accel):
			self.delta_throt_left = self.max_accel

	# set throttle -100 (back) => 0 => +100 (fwd)
	def set_right_throttle(self, newthrottle):
		self.target_throt_right = newthrottle
		self.delta_throt_right = abs((newthrottle - self.current_throt_right) / 10)
		if (self.delta_throt_right > self.max_accel):
			self.delta_throt_right = self.max_accel

	# schedules a stop (dur) seconds from now (both motors)
	def stop_in_x_seconds(self, dur):
		return

	# this should be called every 0.1 seconds when motors are running
	# it refreshes the motor throttle values to implement any accel or decel actions
	def refresh_motors(self):
		at_desired_speed = True
		if (abs(self.target_throt_left - self.current_throt_left) > 1):
			at_desired_speed = False
		if (abs(self.target_throt_right - self.current_throt_right) > 1):
			at_desired_speed = False
		if (at_desired_speed):
			return

		if ((self.target_throt_right - self.current_throt_right) > self.delta_throt_right):
			self.current_throt_right += self.delta_throt_right
		elif ((self.target_throt_right - self.current_throt_right) > 0):
			self.current_throt_right += self.target_throt_right
		elif ((self.target_throt_right - self.current_throt_right) < self.delta_throt_right):
			self.current_throt_right -= self.delta_throt_right
		elif ((self.target_throt_right - self.current_throt_right) < 0):
			self.current_throt_right -= self.target_throt_right
		else:
			self.current_throt_right = self.target_throt_right

		if ((self.target_throt_left - self.current_throt_left) > self.delta_throt_left):
			self.current_throt_left += self.delta_throt_left
		elif ((self.target_throt_left - self.current_throt_left) > 0):
			self.current_throt_left += self.target_throt_left
		elif ((self.target_throt_left - self.current_throt_left) < self.delta_throt_left):
			self.current_throt_left -= self.delta_throt_left
		elif ((self.target_throt_left - self.current_throt_left) < 0):
			self.current_throt_left -= self.target_throt_left
		else:
			self.current_throt_left = self.target_throt_left

		self.screen_dashboard.show_left_throttle(self.current_throt_left)
		self.screen_dashboard.show_right_throttle(self.current_throt_right)


	# this stops both motors, immediately, with no deceleration curv
	def motors_halt(self):
		self.current_throt_left = 0
		self.current_throt_right = 0
		self.target_throt_left = 0
		self.target_throt_right = 0
		self.delta_throt_left = 0
		self.delta_throt_right = 0
		self.increasing_or_decreasing_left = 1	# +1 or -1 multiplier
		self.increasing_or_decreasing_right = 1	# +1 or -1 multiplier
		self.screen_dashboard.show_left_throttle(0)
		self.screen_dashboard.show_right_throttle(0)
"""

