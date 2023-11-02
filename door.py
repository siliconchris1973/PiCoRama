##############################################################
# PiCoRama is a complete set of MicroPython scripts that can #
# handle a diorama - this diorama may contain various lights #
# some of which may be turn ed on / off at certain times,    #
# may flicker or fade. Additionally a motion detectore with  #
# a PIR can be used to initialize tv shows on a oled display #
# These shows consist of small b/w image animations derived  #
# from gifs.                                                 #
#                                                            #
# by c.guenther[at]mac.com                                   #
#                                                            #
# Date: 01.11.2022                                           #
# Version: 1.0                                               #
#                                                            #
##############################################################
#                                                            #
#    DOOR                                                    #
# ---------------------------------------------------------- #
# control the door - open close maintain state (opened /     #
# closed                                                     #
#                                                            #
# ---------------------------------------------------------- #
# V1.0 01.11.2022  initial release                           #
##############################################################

from machine import Pin, PWM
import time
from logging import getLogger
logger = getLogger(__name__)
# SEVERITY = CRITICAL ERROR WARNING INFO DEBUG TRACE CRAZY
logger.setLevel('TRACE')

class door():
    ON = 1
    OFF = 0
    OPEN = ON
    CLOSE = OFF
    
    def __init__(self, setup):
        self.setup = setup
        
        self.use_door_motor = self.setup.getConfigParameter('use_door_motor')
        
        self.ON = self.setup.getConfigParameter('ON')
        self.OFF = self.setup.getConfigParameter('OFF')
        
        self.motor_drive = ''
        self.motor_drive_freq = 50
        
        self.servo_pin = self.setup.getConfigParameter('servo_pin')
        
        self.door_open_pos = self.setup.getConfigParameter('door_opened_position')
        self.door_close_pos = self.setup.getConfigParameter('door_closed_position')
        
        if self.use_door_motor == True:
            self.motor_drive = PWM(Pin(self.servo_pin))
            self.motor_drive.freq(self.motor_drive_freq)
        
        self.door_status = self.CLOSE
        self.door_time = 0
        
        logger.info('init door class')
                  
        logger.debug(' pin ' + str(self.servo_pin)
                    + ' open pos ' + str(self.door_open_pos)
                    + ' close pos ' + str(self.door_close_pos))
        
        self.setServoPos(self.door_close_pos, 100)
        
    # compatibility layer with the other classes
    def toggle(self):
        if self.getStatus() == self.CLOSE:
            self.poweron()
        else:
            self.poweroff()
    def poweron(self):
        self.door_status = self.OPEN
        self.openDoor()
    def poweroff(self):
        self.door_status = self.CLOSE
        self.closeDoor()
    
    def openDoor(self):
        frequency = self.motor_drive_freq
        self.door_time = time.ticks_ms()
        logger.info('opening door')
        logger.debug(' at ' + str(self.door_time))
        logger.trace(' - driving from close pos ' + str(self.door_close_pos)
                      + ' to open pos ' + str(self.door_open_pos)
                      + ' in steps of ' + str(frequency))
        self.driveMotor(self.door_close_pos,self.door_open_pos,frequency)
        
    def closeDoor(self):
        frequency = self.motor_drive_freq*-1
        self.door_time = time.ticks_ms()
        logger.info('closing door')
        logger.debug(' at ' + str(self.door_time))
        logger.trace(' - driving from open pos ' +str(self.door_open_pos)
                      + ' to close pos ' + str(self.door_close_pos)
                      + ' in steps of ' + str(frequency))
        self.driveMotor(self.door_open_pos,self.door_close_pos,frequency)
    
    #
    #  LOW LEVEL driver functions
    #
    def driveMotor(self, start, ende, freq):
        for position in range(start,ende,freq):
            self.setServoPos(position, 10)
    def setServoPos(self, position, sleep_for):
        if self.use_door_motor == True:
            self.motor_drive.duty_u16(position)
        time.sleep_ms(sleep_for)
    def getStatus(self):
        return(self.door_status)
    def getStatusName(self, current_state=True):
        if self.getStatus() == self.CLOSE:
            if current_state == True:
                return('CLOSED')
            else:
                return('opening')
        else:
            if current_state == True:
                return('OPEN')
            else:
                return('closing')