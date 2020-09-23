

import time
import mycolors


class Mode_Calibrate:
	def __init__(self, screen_dashboard, device_motors, device_linesense, device_storage):
		self.screen_dashboard = screen_dashboard
		self.device_motors = device_motors
		self.device_linesense = device_linesense
		self.device_storage = device_storage
		self.throttle_left = 0	# -100 full back, +100=full fwd, 0=stopped
		self.throttle_right = 0	# -100 full back, +100=full fwd, 0=stopped


	# this function initiates mode, runs it till done, then returns text string indicating next mode
	def run_mode(self):
		self.screen_dashboard.show_this_screen()
		status = self.prepare_to_start()
		if (status == "CANCEL"):
			return "MAINMENU"
		self.screen_dashboard.set_text1("Calibrating...")		
		self.screen_dashboard.set_text2("Click A to quit")	
		self.screen_dashboard.set_text3("0", mycolors.PINK, "C")	
		self.screen_dashboard.set_text4("")	
		self.screen_dashboard.set_text5("")	
		self.screen_dashboard.hide_line_position()

		self.device_linesense.calibrate_start()
		self.device_motors.turn_in_place( -75 )

		for i in range(6):
			temp = str(i + 1)
			self.screen_dashboard.set_text3(temp, mycolors.PINK, "C")	
			self.device_motors.turn_in_place( 150 )
			time.sleep(0.2)
			# go back a little farther to left, because it doesn't work as well this way
			self.device_motors.turn_in_place( -160 )

			if (self.device_linesense.calibrate_check()):
				break

		self.device_motors.turn_in_place( 75 )		
		self.device_motors.motors_stop() 

		return "MAINMENU"

	
	def prepare_to_start(self):
		self.screen_dashboard.show_left_throttle(0)
		self.screen_dashboard.show_right_throttle(0)
		self.screen_dashboard.hide_line_position()

		self.screen_dashboard.set_text1("Place robot on track")		
		self.screen_dashboard.set_text2("with sensor over line")	
		self.screen_dashboard.set_text4("Calibrate", mycolors.WHITE, "L")
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

		self.screen_dashboard.set_text4("")		# clear out "calibrate" message
		self.screen_dashboard.set_text5("")		# clear out "starting soon"
		return "READY"


	def display_linesensor(self):
		self.screen_dashboard.show_this_screen()
		self.screen_dashboard.set_text1("Manually move robot")		
		self.screen_dashboard.set_text2("to see sensor values")	

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
		    position = self.device_linesense.get_position() 
		    self.screen_dashboard.set_text3(position, mycolors.PINK, "C")  
		    self.screen_dashboard.show_line_position(position)
		    time.sleep(0.1)
