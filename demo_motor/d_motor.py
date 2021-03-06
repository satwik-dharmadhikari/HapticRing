import serial
import numpy as np
from threading import Thread
import time

class motor(Thread):
	
	def __init__(self):
		Thread.__init__(self)
		self.serial_port = serial.Serial(port='/dev/tty.usbmodem14141', baudrate=115200)
		# # old prototype
		# self.serial_port = serial.Serial(port='/dev/tty.usbmodem14111', baudrate=115200)

		self.trigger_state = 0
		self.target_state = 0
		self.val = 0
		self.max_per_rotation = 0
		self.ready_to_stop_motor = 90
		self.ready_to_stop_sensor = 180
		self.tick_step = 0
		self.profile_step = 0
		self.is_ready = 0
		self.step_count = 0
		self.motor_moving = 0
		# new prototype
		# self.pthreshold_up = 950
		# self.pthreshold_down = 910

		# self.pthreshold_low = 910

		# angrybird
		# self.pthreshold_up = 980
		# self.pthreshold_down = 960

		# self.pthreshold_low = 960

		self.pthreshold_up = 995
		self.pthreshold_down = 950

		self.pthreshold_low = 940

		# self.pthreshold_up = 995
		# self.pthreshold_down = 950

		# self.pthreshold_low = 940

		# old prototype
		# self.pthreshold_up = 670
		# self.pthreshold_down = 650

		# self.pthreshold_low = 520

		self.action_start = 20 #20 degree
		self.action_end =  180  #300 degree

		self.time_tag = time.time()
		self.first_move = True
		self.action_stop = False

		self.custom_profile = []
		self.custom_cur_step = 0  #total step 20? 30? 40?
		self.custom_cur_step_itr = 0

		self.bump_interval = 45

	def close(self):
		self.serial_port.close()

	def write_serial(self, val_string):
		self.serial_port.write(val_string)

	def set_action_stop(self, angle):	
		#know every time the user stop rotating, such that a profile is activated when starting rotating		
		if self.trigger_state == 6 and (self.profile_step == 1 or self.profile_step == 0):
			self.action_stop = True

		if self.trigger_state == 6 and self.profile_step == 1:
			self.val = angle

	def reset(self, target):
		self.trigger_state = 10  #to reset
		self.target_state = target
		self.is_ready = 0

	def noforce(self):
		self.trigger_state = 10
		self.target_state = 1
		self.is_ready = 0
		self.profile_step = 0
		print("1 - noforce")

	def force(self):		
		self.trigger_state = 10
		self.target_state = 2
		self.is_ready = 0
		self.profile_step = 0
		print("2 - force")

	def stop(self):
		self.trigger_state = 10
		self.target_state = 3
		self.is_ready = 0
		self.profile_step = 0
		print("3 - stop")

	def spring(self):
		self.trigger_state = 10
		self.target_state = 4
		self.profile_step = 0
		print("4 - spring")

	def antispring(self):
		self.trigger_state = 10
		self.target_state = 5		
		self.is_ready = 0
		self.profile_step = 0
		print("5 - antispring")

	def tick_bump(self):
		self.trigger_state = 10
		self.target_state = 6
		self.profile_step = 0
		print("6 - bump")

	def custome(self, c_profile):
		self.trigger_state = 10
		self.target_state = 7
		self.profile_step = 0
		self.is_ready = 0
		self.custom_profile = c_profile







	def set_locker(self, b_interval):
		self.trigger_state = 10
		self.target_state = 61
		self.profile_step = 0
		self.is_ready = 0
		self.bump_interval = b_interval
		print("61 - locker bump")

	def set_locker_no_force(self):
		self.trigger_state = 10  #to reset
		self.target_state = 63
		self.is_ready = 0
		self.profile_step = 0
		print("63 - no force")

	def set_locker_stop(self, cval):
		self.trigger_state = 10  #to reset
		self.target_state = 62
		self.is_ready = 0
		self.profile_step = 0
		self.val = cval
		print("62 - stop")




	def set_timer(self):
		self.trigger_state = 10
		self.target_state = 71
		self.is_ready = 0
		self.profile_step = 0
		print("71 - no force")

	def set_timer_force(self):
		self.trigger_state = 10
		self.target_state = 72
		self.is_ready = 0
		self.profile_step = 0
		print("72 - force")

	def set_timer_stop(self):
		self.trigger_state = 10  #to reset
		self.target_state = 73
		self.is_ready = 0
		self.profile_step = 0
		print("73 - stop")

	def set_angry_spring(self):
		self.trigger_state = 10  #to reset
		self.target_state = 81
		self.is_ready = 0
		self.profile_step = 0
		print("81 - spring")

	def set_angry_no_force(self):
		self.trigger_state = 82  #to reset
		self.is_ready = 0
		self.profile_step = 0
		print("82 - no force")


	def set_profile(self, prof):
		if prof == 1:  #no force
			self.noforce()
		elif prof == 2: #force
			self.force()
		elif prof == 3:
			self.stop()
		elif prof == 4:
			self.spring()
		elif prof == 5:
			self.antispring()
		elif prof == 6:
			self.tick_bump()
		elif prof == 0:
			self.reset(0)  #reset to a higher position

	def set_custom_profile(self, c_profile):
		self.custome(c_profile)
		print("customized profile set")


	def get_angle(self, val, pval):  #pval for proximtiy value

		if self.first_move == True and (time.time() - self.time_tag > 2):
			#move a little bit down
			if pval > 600:
				self.serial_port.write("x")
			self.first_move = False
		else:
			#back to the reset position
			if self.trigger_state == 10:  #reset to a higher position
				
				if pval > self.pthreshold_up and self.motor_moving == 0:
					
					self.serial_port.write(".")   #moving down
					self.motor_moving = 1

				elif pval < self.pthreshold_down and self.motor_moving == 0:
					self.serial_port.write("/")  #moving up
					self.motor_moving = 2

				elif (self.motor_moving == 1 and pval < self.pthreshold_up) or (self.motor_moving == 2 and pval > self.pthreshold_down):
					if self.target_state == 0:
						self.trigger_state = 0
					else:
						self.trigger_state = 11
					self.serial_port.write("s")
					#print("reset moving up done")
					self.motor_moving = 0

				elif pval > self.pthreshold_down and pval < self.pthreshold_up:
					if self.target_state == 0:
						self.trigger_state = 0
					else:
						self.trigger_state = 11
					self.serial_port.write("s")
					# print(" reset moving up done")
					self.motor_moving = 0

			elif self.trigger_state == 11:   #reset to a lower position, real get ready
			
				if pval > self.pthreshold_low and self.motor_moving == 0:
					self.serial_port.write(".")   #moving down
					self.motor_moving = 1

				elif pval < self.pthreshold_low:
					self.trigger_state = self.target_state
					#print("reset moving down done")
					if self.trigger_state == 1:
						# print("dong le")
						self.serial_port.write("e")
						# self.serial_port.write("q")
						#self.serial_port.write("q")


					self.target_state = 0
					self.serial_port.write("s")
					self.motor_moving = 0

			elif self.trigger_state == 1:   #no force
				if val>self.action_start and val < self.action_end:
					if self.profile_step == 0:
						# print("set 1")
						self.profile_step = 1
				elif val >=0 and val < 2:
					if self.profile_step == 1:
						self.profile_step =0
						# print("reset 1")
						self.reset(1)


			elif self.trigger_state == 2: #force
				if self.is_ready == 0:
					for i in range(0,2):
						self.serial_port.write("c")
					# self.serial_port.write("x")
					# self.serial_port.write("x")
					# self.serial_port.write("z")
					# self.serial_port.write("z")	
					self.is_ready = 1

				else:
					if val > self.action_start and val < self.action_end:
						if self.profile_step == 0:
							self.profile_step = 1

							if is_recording:
								storage.add_sample(time.time(), val, pval, 4, 0, 0, 0, 0, 0, 0, 0, 0)

					elif val >= 0 and val < 2:
						if self.profile_step == 1:
							self.profile_step = 0
							
							self.reset(2)

			elif self.trigger_state == 3: #stop

				if val > (self.action_start + 25) and val < (self.action_start + 30):
					if self.profile_step == 0:
						self.profile_step = 1
						if is_recording:
							storage.add_sample(time.time(), val, pval, 4, 0, 0, 0, 0, 0, 0, 0, 0)

						for i in range(0,5):
							self.serial_port.write("c")
						# self.serial_port.write("z")

						self.time_tag = time.time()	
						
				elif val >= 0 and val < 40:  #this might not be useful
					if self.profile_step == 1:
						#hold for 2 seconds
						if time.time() - self.time_tag > 2:
							self.reset(3)
							self.profile_step = 0
				
			elif self.trigger_state == 4: #spring

				if val > self.action_start and val < self.action_end:
					if self.profile_step == 0:
						self.profile_step = 1
						if  1 :
							storage.add_sample(time.time(), val, pval, 4, 0, 0, 0, 0, 0, 0, 0, 0)

					val_interval = val - self.val

					if val_interval >=3.00:
						step_interval = (int)(val_interval / 3.00)
						#print(step_interval)
						for x in range(0, step_interval):
							self.serial_port.write("m")  #step down

						self.val = self.val + step_interval * 3.00

				elif val >= 0 and val < 5:
					if self.profile_step == 1:
						self.profile_step = 0
						self.reset(4)

					self.val = self.action_start - 2

			elif self.trigger_state == 5: #antipring
				if self.is_ready == 0:
					#for i in range(0,1):
					self.serial_port.write("c")
					self.serial_port.write("c")
					# self.serial_port.write("x")
					# self.serial_port.write("x")
					# self.serial_port.write("x")
					# self.serial_port.write("z")	
					# self.serial_port.write("z")	
					self.is_ready = 1

				else:

					if val > self.action_start and val < self.action_end:
						if self.profile_step == 0:
							self.profile_step = 1
							if is_recording:
								storage.add_sample(time.time(), val, pval, 4, 0, 0, 0, 0, 0, 0, 0, 0)

						val_interval = val - self.val

						if val_interval >=3.0:
							step_interval = (int)(val_interval / 3.0)
							#print(step_interval)
							for x in range(0, step_interval):
								self.serial_port.write("p")  #step down

							self.val = self.val + step_interval * 3.0

					elif val >= 0 and val < 5:
						if self.profile_step == 1:
							self.profile_step = 0
							self.reset(5)

						self.val = self.action_start - 2

			elif self.trigger_state == 6:  #bump
				if val > self.action_start and val < self.action_end: 
					if self.action_stop:
						if self.profile_step == 0: #or self.profile_step == 1 only the first time
							if val - self.val > 5:  #need to test
								self.profile_step = 2
								if is_recording:
									storage.add_sample(time.time(), val, pval, 41, 0, 0, 0, 0, 0, 0, 0, 0)
								#print("going down")
								for i in range(0,3):
									self.serial_port.write("c")
								self.serial_port.write("z")

								self.time_tag = time.time()	

						if self.profile_step == 2:
							if time.time() - self.time_tag > 0.3:

								#print("going up")
								self.profile_step = 1
								if is_recording:
									storage.add_sample(time.time(), val, pval, 42, 0, 0, 0, 0, 0, 0, 0, 0)
								for i in range(0,3):
									self.serial_port.write("e")
								self.serial_port.write("q")

								self.action_stop = False
						
				elif val >= 0 and val < 5:
					if self.profile_step == 1 or self.profile_step == 2:
						self.reset(6)
						self.profile_step = 0

					self.val = self.action_start

			elif self.trigger_state == 7: #custom profile
				if self.is_ready == 0:
					#pre-set
					if self.custom_profile[0] > 0:
						self.custom_cur_step = self.custom_profile[0]  #current force level
						self.custom_cur_step_itr = 0 #
						for x in range(0, self.custom_cur_step):
								self.serial_port.write("m")  #step down
					self.is_ready = 1
				else:
					if val >= self.action_start and val <= (self.action_end - 20):
						if self.profile_step == 0:
							self.profile_step = 1

						#check which angle is achieved and what is the target step and what is the current step
						self.custom_cur_step_itr = int(val / 5)  # 5 is temp

						if self.custom_cur_step_itr < len(self.custom_profile):
							target_step = self.custom_profile[self.custom_cur_step_itr]

							#do the step
							if target_step > self.custom_cur_step:
								for x in range(self.custom_cur_step, target_step):
									self.serial_port.write("z")
							elif target_step < self.custom_cur_step:
								for x in range(target_step, self.custom_cur_step):
									self.serial_port.write("q")

							self.custom_cur_step = target_step

					elif val >= 0 and val < 5:
						if self.profile_step == 1:
							self.profile_step = 0
							self.reset(7)

			elif self.trigger_state == 61:  #locker bumps
				if val >= 10 and val <= 270:

					if self.profile_step == 0:  #ready to do the bump
						if val - self.val > self.bump_interval or val - self.val < 0:  #need to test
							self.profile_step = 1
							
							#print("going down")
							for i in range(0,3):
								self.serial_port.write("c")
							self.serial_port.write("z")

							self.val = int(val / self.bump_interval) * self.bump_interval 

							self.time_tag = time.time()
		

					elif self.profile_step == 1:  #ready to clear the bump
						if time.time() - self.time_tag > 0.3:

							#print("going up")
							self.profile_step = 0
							
							for i in range(0,3):
								self.serial_port.write("e")
							self.serial_port.write("q")

			elif self.trigger_state == 62:
				if self.profile_step == 0:
					if abs(val - self.val) > 20:
						self.profile_step = 1
						for i in range(0,5):
							self.serial_port.write("c") 
							#this is it.. has to quit


			elif self.trigger_state == 72:  #force
				if self.is_ready == 0:
					for i in range(0,2):
						self.serial_port.write("c")
					self.is_ready = 1
				else:
					#find 90, a full stop
					if self.profile_step == 0:
						if abs(val) > 90:
							print(val)
							print("okokok")
							self.profile_step = 1
							for i in range(0,5):
								self.serial_port.write("c") 

			elif self.trigger_state == 73: #just stop
				if self.profile_step == 0:
					self.profile_step = 1
					for i in range(0,5):
						self.serial_port.write("c") 

			elif self.trigger_state == 81: #spring and antispring
				if abs(val) > self.action_start and abs(val) < self.action_end:
					val_interval = abs(val) - abs(self.val)

					if val_interval >=3.00:
						step_interval = (int)(abs(val_interval) / 3.00)
						#print(step_interval)
						for x in range(0, step_interval):
							self.serial_port.write("m")  #step down

						self.val = self.val + step_interval * 3.00

					elif val_interval <= -3.00:
						step_interval = (int)(abs(val_interval) / 3.0)
						#print(step_interval)
						for x in range(0, step_interval):
							self.serial_port.write("p")  #step down

						self.val = self.val - step_interval * 3.0

				else:
					self.val = self.action_start - 2


				#print("val %s, selfval %s"%(val, self.val))


			elif self.trigger_state == 82:
				if self.profile_step == 0:
					self.profile_step = 1
					for x in range(0, 2):
						self.serial_port.write("e")  #step down






						
				


