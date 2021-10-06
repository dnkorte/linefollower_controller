"""
# Controller for Line-Following Robot
# This runs on an Adafruit Feather M4, with a MiniTFT board.
# It drives a TB6612 to control 2 DC Motors (in blue servo case)
# and talks over I2C to an ItsyBitsy that interfaces a Pololu
# line following sensor
#
# Author(s): Don Korte
# Module:  device_battgery.py reports battery voltages
#   This uses the built-in battery-checking connection for the feather
#   (as documented at https://learn.adafruit.com/adafruit-feather-m4-express-atsamd51/power-management)
#   It also reports voltage on the separate AA cells for motor and line sensor
#   For this purpose, Vbatt is connected through a dual 100k resistive divider
#   to pin A0 on the feather -- the divider is located in the prototyping area
#   on the Feather Doubler board.
#
#   Note that for AAA Alkaline batteries, 4.08v is dead, 5.86 is brand new
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

import board
from analogio import AnalogIn


class Device_Battery:
    def __init__(self):
        self.vbat_feather_pin = AnalogIn(board.VOLTAGE_MONITOR)
        self.vbat_motor_pin = AnalogIn(board.A0)

    def get_vbat_feather(self):
        return (self.vbat_feather_pin.value * 3.3) / 65536 * 2

    def get_vbat_motor(self):
        return (self.vbat_motor_pin.value * 3.3) / 65536 * 2
