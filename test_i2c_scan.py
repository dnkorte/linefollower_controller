#
# program i2c_scan_test.py checks i2c connectivity
# https://learn.adafruit.com/circuitpython-essentials/circuitpython-i2c
# https://learn.adafruit.com/circuitpython-basics-i2c-and-spi/i2c-devices
# 
# CircuitPython demo - I2C scan
# 
# If you run this and it seems to hang, try manually unlocking
# your I2C bus from the REPL with
#  >>> import board 
#  >>> board.I2C().unlock() 

import time
import board

i2c = board.I2C()

while not i2c.try_lock():
    pass

try:
    while True:
        print("I2C addresses found:", [hex(device_address)
              for device_address in i2c.scan()])
        time.sleep(2)

finally:  # unlock the i2c bus when ctrl-c'ing out of the loop
    i2c.unlock()
