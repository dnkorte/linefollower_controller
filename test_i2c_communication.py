"""
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
"""

import time
import board
import struct  # needed to unpack bytearray


def write_and_read(device_addr, command):
    while not i2c.try_lock():
        pass
    i2c.writeto(device_addr, bytes([command]), stop=False)
    # note the size of the buffer tells it how many bytes to read
    # time.sleep(0.005);
    result = bytearray(1)
    i2c.readfrom_into(device_addr, result)
    i2c.unlock()
    onebyte = result[0]
    return onebyte


def write_only(device_addr, command):
    while not i2c.try_lock():
        pass
    i2c.writeto(device_addr, bytes([command]), stop=True)
    i2c.unlock()
    return


def read_7(device_addr):
    while not i2c.try_lock():
        pass
    # note the size of the buffer tells it how many bytes to read
    result = bytearray(7)
    i2c.readfrom_into(device_addr, result)
    i2c.unlock()
    return result


print("starting")

i2c = board.I2C()


for i in range(4):
    write_only(0x32, 0x04)
    # print("turned on LED")
    write_only(0x32, 0x05)
    # print("turned of LED")
    time.sleep(0.001)

for i in range(4):
    value = read_7(0x32)
    time.sleep(0.001)

print(
    "before calibration:",
    value[0],
    value[1],
    value[2],
    value[3],
    value[4],
    value[5],
    value[6],
)

write_only(0x32, 0x01)  # initiate calibration
for i in range(12):
    value = read_7(0x32)
    print(
        "checking:",
        value[0],
        value[1],
        value[2],
        value[3],
        value[4],
        value[5],
        value[6],
    )
    time.sleep(1)


for i in range(80):
    write_only(0x32, 0x02)  # initiate read position
    time.sleep(0.006)
    value = read_7(0x32)
    print(
        "psn check:",
        value[0],
        value[1],
        value[2],
        value[3],
        value[4],
        value[5],
        value[6],
    )
    time.sleep(0.25)

# scan test
if False:
    # Lock the I2C device before we try to scan
    while not i2c.try_lock():
        pass

    print("locked")

    # Print the addresses found once
    print(
        "I2C addresses found:", [hex(device_address) for device_address in i2c.scan()]
    )

    # Unlock I2C now that we're done scanning.
    i2c.unlock()

# calibration test
if False:
    # initiate calibration
    print("initiating calibration")
    write_only(0x32, 0x01)

    # wait a while (actually go turn on a motor and sweep)
    time.sleep(10)

    calibration_status = write_and_read(0x32, 0x03)
    counter = 0
    while (calibration_status != 1) and (counter < 20):
        calibration_status = write_and_read(0x32, 0x03)
        counter += 1
        print(counter, calibration_status)
        time.sleep(1)

    # print("end of calibration loop:", calibration_status)
    if calibration_status == 1:
        print("successfully calibrated")
        counter = 0
        while counter < 50:

            value = write_and_read(0x32, 0x02)
            print(counter, value)

            counter += 1
            time.sleep(0.5)
    else:
        print("unable to complete calibration")

print("done")
