"""
# Controller for Line-Following Robot
# This runs on an Adafruit Feather M4, with a MiniTFT board.  
# It drives a TB6612 to control 2 DC Motors (in blue servo case)
# and talks over I2C to an ItsyBitsy that interfaces a Pololu 
# line following sensor
#
# Author(s): Don Korte
# Module:  screen_summary.py displays a run summary screen
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

from adafruit_display_text import label
import terminalio
import displayio
import time

import mycolors

class Screen_Summary:
    def __init__(self, tft_device, mode_followpath, mode_config, 
        device_storage, device_battery):

        self.this_tft = tft_device
        self.mode_followpath = mode_followpath
        self.mode_config = mode_config
        self.device_storage = device_storage
        self.device_battery = device_battery

        self.this_group = displayio.Group(max_size=16) 

        self.textbox_1 = label.Label(terminalio.FONT, text= "", max_glyphs=36, 
            color=mycolors.WHITE, x=2, y=0)
        self.this_group.append(self.textbox_1)

        self.textbox_2 = label.Label(terminalio.FONT, text= "", max_glyphs=36, 
            color=mycolors.WHITE, x=80, y=0)
        self.this_group.append(self.textbox_2)

        self.textbox_3a = label.Label(terminalio.FONT, text= "", max_glyphs=36, 
            color=mycolors.YELLOW, x=2, y=12)
        self.this_group.append(self.textbox_3a)
        self.textbox_3b = label.Label(terminalio.FONT, text= "", max_glyphs=36, 
            color=mycolors.GREEN, x=80, y=12)
        self.this_group.append(self.textbox_3b)
        self.textbox_3c = label.Label(terminalio.FONT, text= "", max_glyphs=36, 
            color=mycolors.RED, x=120, y=12)
        self.this_group.append(self.textbox_3c)

        self.textbox_5 = label.Label(terminalio.FONT, text= "", max_glyphs=36, 
            color=mycolors.WHITE, x=2, y=24)
        self.this_group.append(self.textbox_5)

        self.textbox_6 = label.Label(terminalio.FONT, text= "", max_glyphs=36, 
            color=mycolors.PINK, x=90, y=24)
        self.this_group.append(self.textbox_6)

        self.textbox_7 = label.Label(terminalio.FONT, text= "", max_glyphs=36, 
            color=mycolors.WHITE, x=2, y=36)
        self.this_group.append(self.textbox_7)

        self.textbox_8 = label.Label(terminalio.FONT, text= "", max_glyphs=36, 
            color=mycolors.PINK, x=90, y=36)
        self.this_group.append(self.textbox_8)

        self.textbox_9 = label.Label(terminalio.FONT, text= "", max_glyphs=36, 
            color=mycolors.WHITE, x=2, y=48)
        self.this_group.append(self.textbox_9)

        self.textbox_10 = label.Label(terminalio.FONT, text= "", max_glyphs=36, 
            color=mycolors.WHITE, x=90, y=48)
        self.this_group.append(self.textbox_10)

        self.textbox_11 = label.Label(terminalio.FONT, text= "", max_glyphs=36, 
            color=mycolors.YELLOW, x=2, y=60)
        self.this_group.append(self.textbox_11)


    def show_this_screen(self):
        self.this_tft.display.show(self.this_group)

    # this function initiates mode, runs it till done, then returns text string indicating next mode
    def run_mode(self):
        self.show_this_screen()
        self.textbox_1.text = ("Run #: " 
            + str(self.mode_followpath.get_run_number()))
        self.textbox_2.text = "Dur: {:.2f} s".format(self.mode_followpath.get_total_run_time())

        pctLeft = int(100 * self.mode_followpath.get_num_left() 
            / self.mode_followpath.get_num_loops())
        pctRight = int(100 * self.mode_followpath.get_num_right() 
            / self.mode_followpath.get_num_loops())
        mytext = "L: {0:d} R: {1:d}".format(pctLeft, pctRight)
        self.textbox_3a.text = mytext

        temp = int(100 * self.mode_followpath.get_num_green() 
            / self.mode_followpath.get_num_loops())
        mytext = "G: {0:d}".format(temp)
        self.textbox_3b.text = mytext
        
        temp = int(100 * self.mode_followpath.get_num_offtrack() 
            / self.mode_followpath.get_num_loops())
        mytext = "OF: {0:d}".format(temp)
        self.textbox_3c.text = mytext
        
        proc_time_per_loop_s = (self.mode_followpath.get_total_proc_time() 
            / self.mode_followpath.get_num_loops())
        mytext = "Proc: {:.1f} mS".format(round(proc_time_per_loop_s*1000, 0))
        self.textbox_5.text = mytext

        self.textbox_6.text = "Vbat F {:.2f}".format(self.device_battery.get_vbat_feather())
        
        free_time_per_loop_s = (self.mode_config.get_loop_speed() 
            - proc_time_per_loop_s)
        mytext = "Free: {:.1f} mS".format(round(free_time_per_loop_s*1000, 0))
        if (free_time_per_loop_s < 0):
            self.textbox_7.color = mycolors.RED
        else:
            self.textbox_7.color = mycolors.WHITE
        self.textbox_7.text = mytext

        self.textbox_8.text = "Vbat M {:.2f}".format(self.device_battery.get_vbat_motor())  
        mytext = "Loop: {:.0f} mS".format(round(self.mode_config.get_loop_speed()*1000, 0))       
        self.textbox_9.text = mytext

        #self.textbox_10.text = "Creep: XX %"
        temp = int(100 * self.mode_followpath.get_num_rxn_limit() 
            / self.mode_followpath.get_num_loops())
        mytext = "RxnLim: {0:d}".format(temp)
        self.textbox_10.text = mytext


        self.textbox_11.text = "A / exit     B / save"

        while True:
            buttons = self.this_tft.buttons

            if buttons.a:
                # print("Button A cycle")
                still_pressed = True
                while  still_pressed:
                    buttons =       self.this_tft.buttons
                    still_pressed = buttons.a
                    time.sleep(0.05)
                # print("released")
                return 

            time.sleep(0.1)

