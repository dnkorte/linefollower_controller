"""
# Controller for Line-Following Robot
# This runs on an Adafruit Feather M4, with a MiniTFT board.  
# It drives a TB6612 to control 2 DC Motors (in blue servo case)
# and talks over I2C to an ItsyBitsy that interfaces a Pololu 
# line following sensor
#
# Author(s): Don Korte
# Module:  mode_followpath.py has the code that controls the actual
#   path-following driving algorithm
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
import math
import mycolors


class Mode_FollowPath:
    def __init__(
        self,
        screen_dashboard,
        device_motors,
        device_linesense,
        device_storage,
        mode_config,
    ):
        self.screen_dashboard = screen_dashboard
        self.device_motors = device_motors
        self.device_linesense = device_linesense
        self.device_storage = device_storage
        self.mode_config = mode_config
        self.lineposition = 0  # initially say its in middle (-125 to +125)
        self.throttle_left = 0  # -100 full back, +100=full fwd, 0=stopped
        self.throttle_right = 0  # -100 full back, +100=full fwd, 0=stopped

        # statistics to keep for summary screen and SD storage
        self.run_number = 0  # run number since powerup
        self.num_green = 0  # number of cycles in green range
        self.num_left = 0  # number of cycles left of center (left of "green" range)
        self.num_right = 0  # number of cycles right of center (right of "green" range)
        self.num_offtrack = (
            0  # number of cycles totally off the track (either direction)
        )
        self.num_rxn_limit = 0  # number of cycles that rxn_rate_limit is surpassed
        self.num_loops = 0  # total number of cycles (loops) on this run
        self.total_proc_time = (
            0  # total seconds in all loops (processing time not including loopdelay)
        )
        self.total_run_time = 0  # total clock duration of run in seconds

    # this function initiates mode, runs it till done, then returns text string indicating next mode
    def run_mode(self):
        self.screen_dashboard.show_this_screen()
        self.run_number += 1
        status = self.prepare_to_start()
        if status == "CANCEL":
            return "MAINMENU"
        self.screen_dashboard.set_text1("", mycolors.RED, "C")
        self.screen_dashboard.set_text2("Click A to quit")
        self.screen_dashboard.set_text3("", mycolors.PINK, "C")
        self.screen_dashboard.set_text4("")
        self.screen_dashboard.set_text5("")

        self.num_green = 0  # number of cycles in green range
        self.num_left = 0  # number of cycles left of center (left of "green" range)
        self.num_right = 0  # number of cycles right of center (right of "green" range)
        self.num_offtrack = (
            0  # number of cycles totally off the track (either direction)
        )
        self.num_rxn_limit = 0  # number of cycles that rxn_rate_limit is surpassed
        self.num_loops = 0  # total number of cycles (loops) on this run
        self.total_proc_time = (
            0  # total seconds in all loops (not including loop_delay)
        )
        self.total_run_time = 0  # total clock duration of run in seconds

        if self.mode_config.get_showdisp() == "No":
            self.screen_dashboard.hide_line_position()
            self.screen_dashboard.set_text4("Runtime Display OFF")
            self.screen_dashboard.set_text5("to reduce process time")

        start_run_time = time.monotonic()

        self.device_motors.motors_accelerate(self.mode_config.throttle)
        self.device_linesense.start_quickposition_check()  # initiate first linesens
        while True:
            start_loop_time = time.monotonic()
            buttons = self.screen_dashboard.this_tft.buttons

            if buttons.a:
                # print("Button A cycle")
                still_pressed = True
                while still_pressed:
                    buttons = self.screen_dashboard.this_tft.buttons
                    still_pressed = buttons.a
                    time.sleep(0.05)
                # print("released")

                self.device_motors.motors_accelerate(0)
                end_run_time = time.monotonic()
                # calculate work length of this run loop in fractional seconds
                self.total_run_time = end_run_time - start_run_time
                return "MAINMENU"

            # slow, normal way...
            # self.lineposition = self.device_linesense.get_position()

            while not self.device_linesense.is_quickposition_ready():
                pass
            self.lineposition = self.device_linesense.get_quickposition()
            # initiate next read (for next loop)
            self.device_linesense.start_quickposition_check()
            self.screen_dashboard.show_line_position(self.lineposition)

            curve = -1 * (self.lineposition - 125) / (125 / self.mode_config.rxn_rate)
            if abs(curve) > self.mode_config.rxn_limit:
                curve = math.copysign(self.mode_config.rxn_limit, curve)
                self.num_rxn_limit += 1

            self.device_motors.move_forward_curved(self.mode_config.throttle, curve)

            # note that little numbers mean i'm LEFT of line (line is to my right)
            # big numbers mean i'm RIGHT of line (line is to my left)
            # numbers < 5 or > 245 are basically OFF the line
            if abs(self.lineposition - 125) < 30:
                self.num_green += 1
            if (self.lineposition < 5) or (self.lineposition > 245):
                self.num_offtrack += 1
            if self.lineposition < 95:
                self.num_left += 1
            if self.lineposition > 155:
                self.num_right += 1
            self.num_loops += 1

            end_loop_time = time.monotonic()
            this_loop_duration = end_loop_time - start_loop_time
            self.total_proc_time += this_loop_duration  # in fractional seconds

            desired_sleep_time = self.mode_config.loop_speed - this_loop_duration
            if desired_sleep_time < 0.001:
                # if processing longer than desired loop set a very tiny
                # sleep time just to let processor breathe...
                desired_sleep_time = 0.001
            time.sleep(desired_sleep_time)

    def prepare_to_start(self):
        self.screen_dashboard.show_L_throttle(0)
        self.screen_dashboard.show_R_throttle(0)
        # self.screen_dashboard.hide_line_position()

        self.screen_dashboard.set_text1("Place robot on track")
        self.screen_dashboard.set_text2("with sensor over line")
        temp = "Run # " + str(self.run_number)
        self.screen_dashboard.set_text4(temp, mycolors.WHITE, "L")
        self.screen_dashboard.set_text5("Starting Soon", mycolors.WHITE, "L")

        time_til_start = 5
        while time_til_start > 0:
            self.screen_dashboard.set_text3(
                "    " + str(time_til_start), mycolors.PINK, "R"
            )
            time_til_start -= 1
            # now wait 1 second, but check for "A" button cancel every 0.1 sec
            for i in range(10):
                buttons = self.screen_dashboard.this_tft.buttons
                if buttons.a:
                    still_pressed = True
                    while still_pressed:
                        buttons = self.screen_dashboard.this_tft.buttons
                        still_pressed = buttons.a
                        time.sleep(0.05)
                    # print("released")
                    return "CANCEL"
                time.sleep(0.1)

        self.screen_dashboard.set_text4("")  # clear out run number
        self.screen_dashboard.set_text5("")  # clear out "starting soon"
        return "READY"

    def get_run_number(self):
        return self.run_number

    def get_num_green(self):
        return self.num_green

    def get_num_left(self):
        return self.num_left

    def get_num_right(self):
        return self.num_right

    def get_num_offtrack(self):
        return self.num_offtrack

    def get_num_rxn_limit(self):
        return self.num_rxn_limit

    def get_num_loops(self):
        return self.num_loops

    def get_total_proc_time(self):
        return self.total_proc_time

    def get_total_run_time(self):
        return self.total_run_time
