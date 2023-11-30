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
# Version: 1.1.1                                             #
#                                                            #
##############################################################
#                                                            #
#    MOTION                                                  #
# ---------------------------------------------------------- #
# check for motion and provide interface to this status      #
#                                                            #
# ---------------------------------------------------------- #
# V1.0 01.11.2022 initial release                            #
# V1.1 30.10.2023 bugfixed class reference                   #
# V1.1.1 30.10.2023 exception handling for hw communication  #
##############################################################
from machine import Pin
import time
import uasyncio as asyncio
from logging import getLogger
logger = getLogger(__name__)
# SEVERITY = CRITICAL ERROR WARNING INFO DEBUG TRACE CRAZY
logger.setLevel('TRACE')

class motion:
    ON = 1
    OFF = 0
    
    def __init__(self, setup):
        self.setup = setup
        
        self.ON = self.setup.getConfigParameter('ON')
        self.OFF = self.setup.getConfigParameter('OFF')
        
        self.pir = ''
        self.use_motion_detector = self.setup.getConfigParameter('use_motion_detector')
        self.show_something_every_x_ms = self.setup.getConfigParameter('show_something_every_x_ms')
        self.last_movement_time = 0
        self.there_is_motion = False
    
        logger.info('init motion class')
        logger.debug('pir pin ' + str(self.setup.getConfigParameter('pir_pin'))
                     + ', ms for forced true='+str(self.show_something_every_x_ms)
                     + ', ms between checks=' +str(self.setup.getConfigParameter('sleep_between_checks_in_ms'))
                     )
        
        # import and initialize the PIR receiver class
        if self.use_motion_detector == True:
            try:
                self.pir = Pin(self.setup.getConfigParameter('pir_pin'), Pin.IN, Pin.PULL_DOWN)
            except Exception as e:
                logger.error('could not communicate with PIR hardware: ' + str(e))
        
        self.last_movement_time = time.ticks_ms()
        #logger.trace('init with movement time at ' + str(self.last_movement_time))
        
        logger.debug('init bg task for motion detection with ' + str(self.setup.getConfigParameter('sleep_between_checks_in_ms')) + 'ms')
        self.my_task = asyncio.create_task(self.motionChecker(self.setup.getConfigParameter('sleep_between_checks_in_ms')))
        
    async def motionChecker(self, milliseconds):
        while True:
            self.there_is_motion=self.setMotionStatus()
            logger.trace('status retrieved as '+str(self.there_is_motion) +' - sleeping for ' + str(milliseconds) + 'ms')
            await asyncio.sleep_ms(milliseconds)
    #
    #   THIS ACTUALLY CHECKS FOR THE PIR VALUE
    #   can be used by the background task or
    #   directly via getMotion()
    #
    def setMotionStatus(self):
        self.there_is_motion = False
        pir_value = self.OFF
        check_time = time.ticks_ms()
        if self.use_motion_detector == True:
            try:
                pir_value = self.pir.value()
                
            except Exception as e:
                logger.error('could not communicate with PIR hardware: ' + str(e))
        else:
            pir_value = self.ON
        
        cur_time_diff = time.ticks_diff(check_time, self.last_movement_time)
        
        # only if show_something_every_x_ms is set to a real value we may occassionally show a show regardless of a movement
        if self.show_something_every_x_ms > -1:
            logger.trace('time '+str(check_time)+' last movement was '+str(self.last_movement_time)+' -> diff: ' + str(cur_time_diff) + ' ms is < = > ' + str(self.show_something_every_x_ms))
            
            if ((pir_value == self.ON) or (cur_time_diff > self.show_something_every_x_ms)):
                logger.trace('motion detected or time run out since last show')
                self.last_movement_time = time.ticks_ms()
                self.there_is_motion = True
        else:
            logger.trace('time '+str(check_time)+' last movement was '+str(self.last_movement_time)+' -> diff: ' + str(cur_time_diff) + ' ms')
            
            if pir_value == self.ON:
                logger.trace('motion detected')
                self.last_movement_time = time.ticks_ms()
                self.there_is_motion = True
        
        logger.debug('pir value=' + str(pir_value) + ', ms since last schow='+str(cur_time_diff)+'ms: motion=' + str(self.there_is_motion))
        
        return(self.there_is_motion)
    #
    #   return current motion status
    #
    def getMotion(self):
        logger.debug('returning '+str(self.there_is_motion)+' for motion value')
        return(self.there_is_motion)