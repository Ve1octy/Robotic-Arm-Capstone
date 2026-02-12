from abc import ABC, abstractmethod
import pigpio
import time
from typing import Union
import numpy as np
import xarm
from time import sleep
from math import exp
from diskcache import Cache
import qwiic_relay
import time
import sys

pi = pigpio.pi()
_MIN_ANGLE = 0
_MAX_ANGLE = 240

class servoComm(ABC):
    
    def __init__(self):
        # Create a cache directory
        self.cache = Cache('./cache_dir')

    def cache_value(self,name, value):
        self.cache[name] = value

    def get_cache(self, name):
        try:
            return self.cache.pop(name, default='default_value')
        except KeyError:
            print(f"Error Key={name} not found in cache.")

    def print_cache(self):
        
        for key in self.cache.iterkeys():
            print(f"{key}: {self.cache[key]}")

    @abstractmethod
    def set_angle(self):
        pass

class uart(servoComm):
    
    def __init__(self, com = '/dev/ttyAMA0', export_code:bool=True):
        self.export_code=export_code
        super().__init__()
        self.com = xarm.Controller(com)
        

        self._position = np.linspace(_MIN_ANGLE,_MAX_ANGLE, 1000)
   
    def set_position(self, servo_id, position, speed = 1500):
        # self.last_position = self.cache_value(servo_id)
        self.com.setPosition(servo_id,position, speed, True)
        self.cache_value(servo_id, position)
    
    def set_angle(self):
        pass

class pwm(servoComm):
    
    def __init__(self, name, lower_limit, upper_limit, max_rotation_deg, dead_band, frequency:int, min_pulse_width:int, 
                 max_pulse_width:int, pin:int):
        self.name = name
        super().__init__()
        self.__LOWER_LIMIT = lower_limit
        self.__UPPER_LIMIT = upper_limit
        self.__MAX_ROTATION_DEG = max_rotation_deg
        self.__DEAD_BAND = dead_band
        self.__FREQUENCY = frequency
        self.__PWM_RANGE = int((1/frequency)*10**6)
        self.__MIN_PULSE_WIDTH = min_pulse_width
        self.__MAX_PULSE_WIDTH = max_pulse_width
        self.__PIN = pin
        self.__init_pos_set = False
        # self.__curr_pulse_width = self.angle_to_pulse_width(initial_angle)
        self.__prev_pulse_width:int
        
        # self.set_initial_angle(initial_angle)
           
    def set_initial_angle(self, current_angle, target_angle):
        self.__curr_pulse_width = self.get_cache(self.name)
        #self.__curr_pulse_width = self.angle_to_pulse_width(current_angle)
        self.set_angle(target_angle, min_delay =0.005, max_delay=0.009, step=True, step_size=0.27)
        
        
          
    def __update_pulse_width(self, pulse_width):
        self.__prev_pulse_width = self.__curr_pulse_width
        self.__curr_pulse_width = pulse_width

    def pulse_width_to_duty_cycle(self, pw:int) -> int:
        """
        Converts the pulse width to duty cycle in nanoseconds.
        
        Args:
            pw(int): the pulse width in microseconds.

        Returns:
            int: duty cycle in nanoseconds.
        """
        return int((pw / self.__PWM_RANGE) * 1000000)  # Convert to nanoseconds

    def angle_to_pulse_width(self, angle: Union[int,float]) -> int:
        """
        Converts the angle to pulse width in microseconds.
        
        Args:
            angle (int,float): The angle in degrees.

        Returns:
            int: pulse width in microseconds.
        """
        return (self.__MIN_PULSE_WIDTH + (angle / self.__MAX_ROTATION_DEG) * (self.__MAX_PULSE_WIDTH - self.__MIN_PULSE_WIDTH))
    
    def get_pulse_width(self):
        return self.__curr_pulse_width

    def get_angle(self):
        return (self.__MAX_ROTATION_DEG*(
            (self.__curr_pulse_width-self.__MIN_PULSE_WIDTH)/
            (self.__MAX_PULSE_WIDTH-self.__MIN_PULSE_WIDTH)))
    
    def move(self, duty_cycle):
        pi.hardware_PWM(self.__PIN, self.__FREQUENCY, duty_cycle)
    
    def stop(self):
        self.move(0)

    def step_down(self):
        new_pw = self.__curr_pulse_width - self.__DEAD_BAND
        new_dc = self.pulse_width_to_duty_cycle(new_pw)
        self.move(new_dc)
        self.__update_pulse_width(new_pw)

    def step_up(self):
        new_pw = self.__curr_pulse_width + self.__DEAD_BAND
        new_dc = self.pulse_width_to_duty_cycle(new_pw)
        self.move(new_dc)
        self.__update_pulse_width(new_pw)

    def set_angle(self, angle, min_delay =0.001, max_delay=0.005, step=True, step_size=0.5):
        
        """
        Set the servo to a specific angle between 0° and 270°.
        """
        #30 to 210 since realistically only have 180 deg to work with
        if angle < self.__LOWER_LIMIT or angle > self.__UPPER_LIMIT:
            print("Angle out of range. Must be between 0 and 270 degrees.")
            return
        
        if not self.__init_pos_set:
            self.__curr_pulse_width = self.get_cache(self.name)
            
            self.__init_pos_set = True
    
            
        # Convert pulse width to duty cycle percentage (1% = 10000 in pigpio hardware_PWM)
        target_pw = self.angle_to_pulse_width(angle)
        current_pw = self.__curr_pulse_width
        end_pw = target_pw
        # Move gradually
        
        step_size_pw = self.angle_to_pulse_width(step_size)-self.__MIN_PULSE_WIDTH
        
        if current_pw > target_pw:
            pulse_step = np.arange(current_pw,target_pw,-1* step_size_pw)      
        else:
            pulse_step = np.arange(current_pw,target_pw,step_size_pw)  
        
        for step in pulse_step:
            duty_cycle = self.pulse_width_to_duty_cycle(step) #int((pw / self.__PWM_RANGE) * 1000000)  # Convert to nanoseconds
            #print(step,"\t", duty_cycle, "\t")
            self.move(duty_cycle)
            remaining_movement=abs(target_pw-step)
            
            # delay = max_delay - (remaining_movement/abs(target_pw-current_pw))*(max_delay-min_delay)
            k = 6
            x = remaining_movement/abs(target_pw-current_pw)
            delay = min_delay + (max_delay - min_delay) * 1/(1+exp(k*(x-0.5)))
            
            sleep(delay)
        
        # Ensure final position
        end_dc = self.pulse_width_to_duty_cycle(end_pw)
        self.cache_value(self.name, end_pw)
        self.move(end_dc)
        self.__update_pulse_width(end_pw)
        self.stop()


def run_elbow(angle_entered): 
    angle = int(angle_entered)
    # elbow.set_angle(120, min_delay =0.001, max_delay=0.009, step=True, step_size=0.27)

        
    elbow.set_angle(angle, min_delay =0.010, max_delay=0.02, step=True, step_size=0.27)
    
    #elbow.stop()



def run_shoulder(angle_entered):
    

    angle = int(angle_entered)
    shoulder.set_angle(angle,min_delay =0.005, max_delay=0.015, step=True, step_size=0.27)

    shoulder.stop()

def run_bus(id_entered, angle_entered):
    id = id_entered
    angle = angle_entered
    angle = int(angle)
    id = int(id)
    bus_servo.set_position(id, angle)


try:
    myRelay = qwiic_relay.QwiicRelay(qwiic_relay.SINGLE_RELAY_DEFUALT_ADDR)
    elbow = pwm(name='elbow', lower_limit=30, upper_limit=210, max_rotation_deg=270, dead_band=0.5, frequency=50, min_pulse_width=500, max_pulse_width=2500, pin=18)
    shoulder = pwm(name='shoulder', lower_limit=0, upper_limit=270, max_rotation_deg=270, dead_band=0.5, frequency=50, min_pulse_width=500, max_pulse_width=2500, pin=13)
    bus_servo = uart()

    #Set elbow to 120/124 (Base case to start, rest of arm will sit in a way that shoudlnt hit anything)
    run_elbow(120)

    #Cycle 1 **************************
    #Set angle for tray position 1
    #for now shoulder 120
    # run_shoulder(120)
    # time.sleep(1)
    run_shoulder(148)
    #Set hiwonders to be ready to pick up
    run_bus(1,294)
    run_bus(2, 97)
    
    
    #Drop elbow for contact
    run_elbow(78)

    myRelay.set_relay_on()
    time.sleep(1)
    #Raise
    run_elbow(110)
    #Swing to container
    run_shoulder(15)
    #Lower elbow
    run_elbow(87)
    
    #Turn off
    #vac_off()
    myRelay.set_relay_off()
    time.sleep(.7)
    #Raise elbow
    run_elbow(110)

    #Cycle 2 **************************
    #Set angle for tray position 2
    run_shoulder(143)
    #Set hiwonders to be ready to pick up
    # run_bus(1, 400)
    # run_bus(2, 400)
    #Drop elbow for contact
    run_elbow(78)

    #Turn on
    #vac_on()
    myRelay.set_relay_on()
    sleep(1)
    #Raise
    run_elbow(110)
    #Swing to container
    run_shoulder(15)
    #Lower elbow
    run_elbow(87)
    
    #Turn off
    #vac_off()
    myRelay.set_relay_off()
    time.sleep(.7)
    #Raise elbow
    run_elbow(110)

#Cycle 3 **************************
    #Set angle for tray position 2
    run_shoulder(138)
    #Set hiwonders to be ready to pick up
    # run_bus(1, 400)
    # run_bus(2, 400)
    #Drop elbow for contact
    run_elbow(78)

    #Turn on
    #vac_on()
    myRelay.set_relay_on()
    sleep(1)
    #Raise
    run_elbow(110)
    #Swing to container
    run_shoulder(15)
    #Lower elbow
    run_elbow(87)
    
    #Turn off
    #vac_off()
    myRelay.set_relay_off()
    time.sleep(.7)
    #Raise elbow
    run_elbow(110)

#Cycle 4 **************************
    #Set angle for tray position 1
    #for now shoulder 120
    # run_shoulder(120)
    # time.sleep(1)
    run_shoulder(148)
    #Set hiwonders to be ready to pick up
    run_bus(1,234)
    run_bus(2, 130)
    #Drop elbow for contact
    run_elbow(86)

    myRelay.set_relay_on()
    time.sleep(1)
    #Raise
    run_elbow(110)
    #Swing to container
    run_shoulder(15)
    #Lower elbow
    run_elbow(93)
    
    #Turn off
    #vac_off()
    myRelay.set_relay_off()
    time.sleep(.7)
    #Raise elbow
    run_elbow(110)

    #Cycle 5 **************************
    #Set angle for tray position 2
    run_shoulder(143)
    #Set hiwonders to be ready to pick up
    # run_bus(1, 400)
    # run_bus(2, 400)
    #Drop elbow for contact
    run_elbow(85)

    #Turn on
    #vac_on()
    myRelay.set_relay_on()
    sleep(1)
    #Raise
    run_elbow(110)
    #Swing to container
    run_shoulder(15)
    #Lower elbow
    run_elbow(93)
    
    #Turn off
    #vac_off()
    myRelay.set_relay_off()
    time.sleep(.7)
    #Raise elbow
    run_elbow(110)

#Cycle 6 **************************
    #Set angle for tray position 2
    run_shoulder(137)
    #Set hiwonders to be ready to pick up
    # run_bus(1, 400)
    # run_bus(2, 400)
    #Drop elbow for contact
    run_elbow(86)   

    #Turn on
    #vac_on()
    myRelay.set_relay_on()
    sleep(1)
    #Raise
    run_elbow(110)
    #Swing to container
    run_shoulder(15)
    #Lower elbow
    run_elbow(93)
    
    #Turn off
    #vac_off()
    myRelay.set_relay_off()
    time.sleep(.7)
    #Raise elbow
    run_elbow(110)


except KeyboardInterrupt:
    print("\nExiting program...")


finally:
    # pi.hardware_PWM(18,0,0)
    elbow.cache.close()
    shoulder.cache.close()
    pi.stop()
