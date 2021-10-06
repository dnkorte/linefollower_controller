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
#    so a 360 degree turn is 12 in of circumference or 1 second
#    a 90 degree turn is approx 0.25 sec.  Note also that these motors
#    are basically too fast for this application -- they need to run at 
#    40% throttle or less for reasonable speeds -- and 20% (or thereabouts
#    is the very bottom end for these motors -- they have no torque or 
#    reliability at this speed)
# 
# Note (dnk) with a 6v Vmot, 0.20 throttle is about the slowest they can go
#    
# reference adafruit motor library guide: 
#   https://circuitpython.readthedocs.io/projects/motor/en/latest/api.html
#   The TB6612 boards feature three inputs XIN1, XIN2 and PWMX. Since we 
#   PWM the INs directly its expected that the PWM pin is consistently high.
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
        self.max_accel = 10  # max allowed acceleration in pct per 0.1 sec
        self.cur_throt_L = 0
        self.cur_throt_R = 0

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
        # the faster motor should be set to whatever it takes to reduces its
        # speed to match slower motor
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

        self.max_delta_throt = 0.1

    #
    # #############################################################################
    # for motion commands, throttle values are -1.0 (back) => 0 => 1.0 (forward)
    # #############################################################################
    #

    def move_forward(self, targetThrottle):
        self.cur_throt_L = targetThrottle
        self.cur_throt_R = targetThrottle
        self.motorL.throttle = self.cur_throt_L * self.motorCalibrateL
        self.motorR.throttle = self.cur_throt_R * self.motorCalibrateR
        self.screen_dashboard.show_L_throttle(self.cur_throt_L)
        self.screen_dashboard.show_R_throttle(self.cur_throt_R)

    def move_backward(self, targetThrottle):
        self.cur_throt_L = targetThrottle * (-1)
        self.cur_throt_R = targetThrottle * (-1)
        self.motorL.throttle = self.cur_throt_L * self.motorCalibrateL
        self.motorR.throttle = self.cur_throt_R * self.motorCalibrateR
        self.screen_dashboard.show_L_throttle(self.cur_throt_L)
        self.screen_dashboard.show_R_throttle(self.cur_throt_R)

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
        self.cur_throt_L = targetThrottle + (targetThrottle * curve / 2)
        if self.cur_throt_L < 0:
            self.cur_throt_L = 0
        if self.cur_throt_L > 1:
            self.cur_throt_L = 1
        self.cur_throt_R = targetThrottle - (targetThrottle * curve / 2)
        if self.cur_throt_R < 0:
            self.cur_throt_R = 0
        if self.cur_throt_R > 1:
            self.cur_throt_R = 1
        self.motorL.throttle = self.cur_throt_L * self.motorCalibrateL
        self.motorR.throttle = self.cur_throt_R * self.motorCalibrateR
        self.screen_dashboard.show_L_throttle(self.cur_throt_L)
        self.screen_dashboard.show_R_throttle(self.cur_throt_R)

    #
    # function motors_accelerate() is like move forward accept that instead of
    # immediately setting throttle to the targetThrottle it honors a
    # "max acceleration rate" configuration parameter and steps gradually to
    # the targetThrottle.
    #
    # it returns# the number of seconds that it took to get there.
    #
    def motors_accelerate(self, targetThrottle):
        if abs(abs(targetThrottle) - abs(self.cur_throt_L)) < self.max_delta_throt:
            # new throttle is close to current to can just go there
            # pass
            print("already close enough - just going to:", targetThrottle)
        elif targetThrottle < self.cur_throt_L:
            # will have to go in steps, and they will be steps DOWN
            while (self.cur_throt_L - targetThrottle) > self.max_delta_throt:
                self.cur_throt_L = self.cur_throt_L - self.max_delta_throt
                self.cur_throt_R = self.cur_throt_R - self.max_delta_throt
                self.motorL.throttle = self.cur_throt_L * self.motorCalibrateL
                self.motorR.throttle = self.cur_throt_R * self.motorCalibrateR
                self.screen_dashboard.show_L_throttle(self.cur_throt_L)
                self.screen_dashboard.show_R_throttle(self.cur_throt_R)
                # print("stepping up:", self.cur_throt_L)
                time.sleep(0.1)
        else:
            # will have to go in steps, and the will be steps UP
            while (targetThrottle - self.cur_throt_L) > self.max_delta_throt:
                self.cur_throt_L = self.cur_throt_L + self.max_delta_throt
                self.cur_throt_R = self.cur_throt_R + self.max_delta_throt
                self.motorL.throttle = self.cur_throt_L * self.motorCalibrateL
                self.motorR.throttle = self.cur_throt_R * self.motorCalibrateR
                self.screen_dashboard.show_L_throttle(self.cur_throt_L)
                self.screen_dashboard.show_R_throttle(self.cur_throt_R)
                # print("stepping down:", self.cur_throt_L)
                time.sleep(0.1)

        self.cur_throt_L = targetThrottle
        self.cur_throt_R = targetThrottle
        self.motorL.throttle = self.cur_throt_L * self.motorCalibrateL
        self.motorR.throttle = self.cur_throt_R * self.motorCalibrateR
        self.screen_dashboard.show_L_throttle(self.cur_throt_L)
        self.screen_dashboard.show_R_throttle(self.cur_throt_R)

    #
    # function turn_in_place() spins the robot "in place" (w/o forward movement)
    # degrees is amount to turn, in degrees (-) is left, (+) is right
    #

    def turn_in_place(self, degrees):
        self.cur_throt_L = math.copysign(self.throttle_for_360, degrees)
        self.cur_throt_R = math.copysign(self.throttle_for_360, degrees) * (-1)
        self.motorL.throttle = self.cur_throt_L * self.motorCalibrateL_turn
        self.motorR.throttle = self.cur_throt_R * self.motorCalibrateR_turn
        # self.motorL.throttle = self.cur_throt_L
        # self.motorR.throttle = self.cur_throt_R
        self.screen_dashboard.show_L_throttle(self.cur_throt_L)
        self.screen_dashboard.show_R_throttle(self.cur_throt_R)

        duration = abs(degrees * self.seconds_for_360) / 360
        time.sleep(duration)

        self.motors_stop()

    #
    # function motors_stop() causes both motors to stop turning immediately
    # no deceleration curve is applied
    #
    def motors_stop(self):
        self.cur_throt_L = 0
        self.cur_throt_R = 0
        self.motorL.throttle = self.cur_throt_L * self.motorCalibrateL
        self.motorR.throttle = self.cur_throt_R * self.motorCalibrateR
        self.screen_dashboard.show_L_throttle(self.cur_throt_L)
        self.screen_dashboard.show_R_throttle(self.cur_throt_R)
