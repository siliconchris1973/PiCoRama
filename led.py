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
# Date: 30.10.2023                                           #
# Version: 1.1                                               #
#                                                            #
##############################################################
#                                                            #
#     LED                                                    #
# ---------------------------------------------------------- #
#                                                            #
# Low Level class powering individual leds                   #
# provides FADING, FLICKERING and TIMED functions            #
#                                                            #
#                                                            #
# ---------------------------------------------------------- #
# V1.0 01.11.2022 initial release                            #
# V1.1 30.10.2023 changed log wording                        #
##############################################################
from machine import Pin, PWM
import time, random
import uasyncio as asyncio
from logging import getLogger
logger = getLogger(__name__)
# SEVERITY = CRITICAL ERROR WARNING INFO DEBUG TRACE CRAZY
logger.setLevel('WARNING') 

class led:
    ON = 1
    OFF = 0
    
    def __init__(self, setup, the_led_pin=1, led_name='unnamed', min_on_time=-1, max_on_time=-1, min_off_time=-1, max_off_time=-1, next_check_timer=3000, always_on=False, is_of_type='standard'):
        self.setup = setup
        
        self.ON = self.setup.getConfigParameter('ON')
        self.OFF = self.setup.getConfigParameter('OFF')
        
        # NOW SETUP THE LED ITSELF
        self.the_led = ''
        self.led_name = led_name
        self.always_on = always_on
        self.is_of_type = is_of_type
        self.led_status = self.OFF
    
        self.start_time = 0
        self.stop_time = 0
        self.min_on_timer = min_on_time
        self.max_on_timer = max_on_time
        self.min_off_timer = min_off_time
        self.max_off_timer = max_off_time
        self.next_check_timer = next_check_timer
        self.next_check = 0
        self.random_state_chang_at = 0
        
        self.my_task = '' # contains the task object once a flicker led is put in the background
        self.bg_task_active = False
    
        logger.info('init led class for ' + str(self.led_name))
        logger.debug('pin ' + str(the_led_pin)
                  + ' min on ' + str(self.min_on_timer) 
                  + ' max on ' + str(self.max_on_timer)
                  + ' min off ' + str(self.min_off_timer)
                  + ' max off ' + str(self.max_off_timer)
                  + ' check ' + str(self.next_check_timer)
                  + ' always on ' + str(self.always_on)
                  + ' type ' + str(self.is_of_type))
        
        if self.is_of_type == 'fader':
            logger.trace('setting PWM frequency to 1000 for ' + str(self.led_name) + ' on pin ' + str(the_led_pin))
            self.the_led = PWM(Pin(the_led_pin, Pin.OUT))
            self.the_led.freq(1000)
        else:
            logger.trace('setting pin '+str(the_led_pin)+' for ' + str(self.led_name))
            self.the_led = Pin(the_led_pin, Pin.OUT)
    
    #
    #   Timed FUNCTION
    #
    async def timed(self, sleep_for=3600000):
        logger.debug('timed background task active for led ' + str(self.led_name))
        self.bg_task_active = True
        tar_y = self.min_on_timer[0]
        tar_m = self.min_on_timer[1]
        tar_d = self.min_on_timer[2]
        logger.trace('this light shall be turned on at '
                  + str(tar_d) + '.'
                  + str(tar_m) + '.'
                  + str(tar_y))
        while True:
            pwr_on = False
            now_time = time.ticks_ms()
            if now_time > self.next_check:
                cur_y = time.gmtime()[0]
                cur_m = time.gmtime()[1]
                cur_d = time.gmtime()[2]
                
                logger.crazy('now it is '
                          + str(cur_d) + '.'
                          + str(cur_m) + '.'
                          + str(cur_y))
                
                if int(cur_y) >= int(tar_y):
                    if int(cur_m) > int(tar_m):
                        pwr_on = True
                    elif int(cur_m) == int(tar_m):
                        if int(cur_d) >= int(tar_d):
                            pwr_on = True
                if pwr_on == True and self.getStatus() == self.OFF:
                    logger.debug('powering on ' + str(self.led_name))
                    self.the_led.value(self.ON)
                    self.led_status = self.ON
                else:
                    logger.trace('keeping '+str(self.led_name)+' off ')
                    self.the_led.value(self.OFF)
                    self.led_status = self.OFF
            await asyncio.sleep_ms(sleep_for) # sleep(1 minute)
    
    
    #
    #   FADER FUNCTION
    #
    async def fader(self, sleep_for=1):
        logger.debug('fading background task active for led ' + str(self.led_name))
        self.bg_task_active = True
        self.led_status = self.ON
        while True:
            for duty in range(self.min_on_timer, self.max_on_timer, self.next_check_timer):
                self.the_led.duty_u16(duty)
                await asyncio.sleep_ms(sleep_for) # sleep(0.0001)
            await asyncio.sleep_ms(1000)
            for duty in range(self.max_off_timer, self.min_off_timer, -self.next_check_timer):
                self.the_led.duty_u16(duty)
                await asyncio.sleep_ms(sleep_for) # sleep(0.0001)
            await asyncio.sleep_ms(1000)
    #
    #   FLICKER FUNCTION
    #
    async def flicker(self, sleep_for=500):
        logger.debug('flicker background task active for led ' + str(self.led_name))
        self.bg_task_active = True
        
        while True:
            now_time = time.ticks_ms()
            # we check in case the current ms is higher than the ms of the last check plus a timer (30 seconds) stored in next_check
            if now_time > self.next_check:
                # now that we check, make sure to increase the next check timer
                self.next_check = now_time + self.next_check_timer
                
                # in case the current time is more than the maximum on or off time determined during
                # the last state change, we switch the state and store the new now timer
                if now_time > (self.getStateSince() + self.random_state_chang_at):
                    self.random_state_chang_at = self.getRandomTimer()
                    
                    logger.trace(self.led_name + ' is '
                              + self.getStateName(True) + ' since '
                              + str(self.getStateSince())
                              + ' now is ' + str(now_time) + ' ('+str(now_time-self.getStateSince())+') switching state after '
                              + str(self.random_state_chang_at) + ' ms = '
                              + str(now_time + self.random_state_chang_at)
                              + ' to ' + self.getStateName(False))
                    if self.led_status == self.ON:
                        self.the_led.value(self.OFF)
                        self.led_status = self.OFF
                    else:
                        self.the_led.value(self.ON)
                        self.led_status = self.ON
                else:
                    logger.trace('keeping ' 
                              + self.led_name + ' '
                              + self.getStateName(True) + ' at '
                              + str(now_time))
            await asyncio.sleep_ms(sleep_for)
            
    #
    #   PUT FADER OR FLICKER FUNCTION IN BACKGROUND
    #
    async def background(self):
        logger.trace('activation of background task requested for ' + str(self.is_of_type) + ' light ' + str(self.led_name))
        self.bg_task_active = True
        if self.is_of_type == 'flicker':
            self.my_task = asyncio.create_task(self.flicker(500))
        elif self.is_of_type == 'fader':
            self.my_task = asyncio.create_task(self.fader(10))
        elif self.is_of_type == 'timed':
            self.my_task = asyncio.create_task(self.timed(self.next_check_timer))
        
    def cancelBackground(self):
        logger.trace('cancellation of background task requested for ' + str(self.is_of_type) + ' light ' + str(self.led_name))
        self.bg_task_active = False
        asyncio.Task(self.my_task).cancel()
        if self.is_of_type == 'fader':
            self.the_led.duty_u16(self.OFF)
        else:
            self.the_led.value(self.OFF)
    
    #
    #   LOW LEVEL DRIVER FUNCTIONS
    #
    def poweron(self):
        logger.trace('low level power on function for ' + str(self.led_name))
        self.start_time = time.ticks_ms()
        
        if self.is_of_type == 'standard':
            self.led_status = self.ON
            self.the_led.value(self.ON)
        else:
            asyncio.run(self.background())
        return(self.led_status)
    def poweroff(self):
        logger.trace('low level power off function for ' + str(self.led_name))
        self.stop_time = time.ticks_ms()
        
        if self.is_of_type == 'standard':
            self.led_status = self.OFF
            self.the_led.value(self.OFF)
        else:
            self.cancelBackground()
        return(self.led_status)
    def getName(self):
        return(self.led_name)
    def getStateName(self, current=True):
        if self.led_status == self.OFF:
            if current == True:
                return('OFF')
            else:
                return('ON')
        else:
            if current == True:
                return('ON')
            else:
                return('OFF')
    def getStatus(self):
        return(self.led_status)
    def getStateSince(self):
        if self.getStatus == self.OFF:
            return(int(self.stop_time))
        else:
            return(int(self.start_time))
    def getRandomTimer(self):
        if self.led_status == self.ON:
            random_timer = random.randint(self.min_on_timer,self.max_on_timer)
        elif self.led_status == self.OFF:
            random_timer = random.randint(self.min_off_timer,self.max_off_timer)
        else:
            random_timer = 0
        return(random_timer)
    