#
# module device_motors manages motors
# 
# Author(s):  Don Korte
# Repository: https://github.com/dnkorte/xxxx
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

import time
import board

class Device_LineSense:
	def __init__(self, screen_dashboard):
		# print("faked out i2c init")
		# return

		self.i2c_address = 0x32
		self.i2c = board.I2C()
		self.calibrated = False
		self.position = 125
		self.device_registers = self._read_7()
		self.sensor_type = self.device_registers[0]
		self.read_delay = self.device_registers[1]
		self.module_id = self.device_registers[2]
		if (self.module_id != 83):
			raise RuntimeError("Line Sensor is not the expected module")
		self.screen_dashboard = screen_dashboard

		print("sensor type:", self.sensor_type)
		print("read_delay:", self.read_delay)
		print("module id:", self.module_id)


	def _write_cmd(self, command):
		while not self.i2c.try_lock():
			pass
		self.i2c.writeto(self.i2c_address, bytes([command]), stop=True)
		self.i2c.unlock()
		return

	def _read_7(self):
		while not self.i2c.try_lock():
			pass
		# note the size of the buffer tells it how many bytes to read
		result = bytearray(7)		
		self.i2c.readfrom_into(self.i2c_address, result)
		self.i2c.unlock()
		return result


	def calibrate_start(self):
		self.calibrated = False
		self._write_cmd(0x01)
		# make sure we don't read anything til after its noticed the command
		time.sleep(0.001)

	def calibrate_check(self):
		self.device_registers = self._read_7()
		temp = self.device_registers[3]
		if (temp == 1):
			self.calibrated = True
		else:
			self.calibrated = False
		return self.calibrated

	# returns signed integer 0 => +250; 125 indicates line is centered
	# position < 125 indicate steer left is suggested
	# position > 125  indicate steer right is suggested
	def get_position(self):
		self._write_cmd(0x02)					# initiate read
		time.sleep(0.001 * self.read_delay)		# give it time to finish
		self.device_registers = self._read_7()	# read the result
		self.position = self.device_registers[5]	
		print("raw position:", self.position)
		return self.position  
