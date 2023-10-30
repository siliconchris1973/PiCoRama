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
#    LIGHTS                                                  #
# ---------------------------------------------------------- #
# use the low level led class to drive arrays of lights      #
# can handle up to 5 standard, fader, flicker and timed leds #
# as configured in the setup.py file                         #
#                                                            #
# ---------------------------------------------------------- #
# V1.0 01.11.2022 initial release                            #
# V1.1 30.10.2023 removed specific names of standard leds to #
#                 make it more usabel in a generic context   #
##############################################################
import uasyncio as asyncio
from logging import getLogger
logger = getLogger(__name__)
logger.setLevel('INFO')

from led import led

class lights:
    ON = 1
    OFF = 0
    
    def __init__(self, setup):
        self.setup = setup
        
        self.ON = self.setup.getConfigParameter('ON')
        self.OFF = self.setup.getConfigParameter('OFF')
        
        logger.info('init lights class')
        
        #
        #   SETUP ALL THE LIGHTS
        #
        self.standard_leds = []
        self.timed_leds = []
        self.flicker_leds = []
        self.fader_leds = []
        self.standard_led_5 = ''
        if self.setup.getConfigElementFromList('standard_led_1', 'PIN') != -1:
            logger.debug('init standard led 1')
            self.standard_leds.append(led(self.setup
                                    , self.setup.getConfigElementFromList('standard_led_1', 'PIN')
                                    , self.setup.getConfigElementFromList('standard_led_1', 'NAME')
                                    , self.setup.getConfigElementFromList('standard_led_1', 'led_min_on_timer')
                                    , self.setup.getConfigElementFromList('standard_led_1', 'led_max_on_timer')
                                    , self.setup.getConfigElementFromList('standard_led_1', 'led_min_off_timer')
                                    , self.setup.getConfigElementFromList('standard_led_1', 'led_max_off_timer')
                                    , self.setup.getConfigElementFromList('standard_led_1', 'led_check_timer')
                                    , self.setup.getConfigElementFromList('standard_led_1', 'always_on')
                                    , self.setup.getConfigElementFromList('standard_led_1', 'is_of_type')
                                    ))
        if self.setup.getConfigElementFromList('standard_led_2', 'PIN') != -1:
            logger.debug('init standard led 2')
            self.standard_leds.append(led(self.setup
                                    , self.setup.getConfigElementFromList('standard_led_2', 'PIN')
                                    , self.setup.getConfigElementFromList('standard_led_2', 'NAME')
                                    , self.setup.getConfigElementFromList('standard_led_2', 'led_min_on_timer')
                                    , self.setup.getConfigElementFromList('standard_led_2', 'led_max_on_timer')
                                    , self.setup.getConfigElementFromList('standard_led_2', 'led_min_off_timer')
                                    , self.setup.getConfigElementFromList('standard_led_2', 'led_max_off_timer')
                                    , self.setup.getConfigElementFromList('standard_led_2', 'led_check_timer')
                                    , self.setup.getConfigElementFromList('standard_led_2', 'always_on')
                                    , self.setup.getConfigElementFromList('standard_led_2', 'is_of_type')
                                    ))
        if self.setup.getConfigElementFromList('standard_led_3', 'PIN') != -1:
            logger.debug('standard led 3')
            self.standard_leds.append(led(self.setup
                                    , self.setup.getConfigElementFromList('standard_led_3', 'PIN')
                                    , self.setup.getConfigElementFromList('standard_led_3', 'NAME')
                                    , self.setup.getConfigElementFromList('standard_led_3', 'led_min_on_timer')
                                    , self.setup.getConfigElementFromList('standard_led_3', 'led_max_on_timer')
                                    , self.setup.getConfigElementFromList('standard_led_3', 'led_min_off_timer')
                                    , self.setup.getConfigElementFromList('standard_led_3', 'led_max_off_timer')
                                    , self.setup.getConfigElementFromList('standard_led_3', 'led_check_timer')
                                    , self.setup.getConfigElementFromList('standard_led_3', 'always_on')
                                    , self.setup.getConfigElementFromList('standard_led_3', 'is_of_type')
                                    ))
        if self.setup.getConfigElementFromList('standard_led_4', 'PIN') != -1:
            logger.debug('standard led 4')
            self.standard_leds.append(led(self.setup
                                    , self.setup.getConfigElementFromList('standard_led_4', 'PIN')
                                    , self.setup.getConfigElementFromList('standard_led_4', 'NAME')
                                    , self.setup.getConfigElementFromList('standard_led_4', 'led_min_on_timer')
                                    , self.setup.getConfigElementFromList('standard_led_4', 'led_max_on_timer')
                                    , self.setup.getConfigElementFromList('standard_led_4', 'led_min_off_timer')
                                    , self.setup.getConfigElementFromList('standard_led_4', 'led_max_off_timer')
                                    , self.setup.getConfigElementFromList('standard_led_4', 'led_check_timer')
                                    , self.setup.getConfigElementFromList('standard_led_4', 'always_on')
                                    , self.setup.getConfigElementFromList('standard_led_4', 'is_of_type')
                                    ))
        if self.setup.getConfigElementFromList('standard_led_5', 'PIN') != -1:
            logger.debug('init standard led 5')
            self.standard_led_5 = led(self.setup
                                , self.setup.getConfigElementFromList('standard_led_5', 'PIN')
                                , self.setup.getConfigElementFromList('standard_led_5', 'NAME')
                                , self.setup.getConfigElementFromList('standard_led_5', 'led_min_on_timer')
                                , self.setup.getConfigElementFromList('standard_led_5', 'led_max_on_timer')
                                , self.setup.getConfigElementFromList('standard_led_5', 'led_min_off_timer')
                                , self.setup.getConfigElementFromList('standard_led_5', 'led_max_off_timer')
                                , self.setup.getConfigElementFromList('standard_led_5', 'led_check_timer')
                                , self.setup.getConfigElementFromList('standard_led_5', 'always_on')
                                , self.setup.getConfigElementFromList('standard_led_5', 'is_of_type')
                                )
        
        #
        #   THE TIMED LIGHTS
        #
        if self.setup.getConfigElementFromList('timed_led_1', 'PIN') != -1:
            logger.debug('init timed 1 light')
            self.timed_leds.append(led(self.setup
                                    , self.setup.getConfigElementFromList('timed_led_1', 'PIN')
                                    , self.setup.getConfigElementFromList('timed_led_1', 'NAME')
                                    , self.setup.getConfigElementFromList('timed_led_1', 'led_min_on_timer')
                                    , self.setup.getConfigElementFromList('timed_led_1', 'led_max_on_timer')
                                    , self.setup.getConfigElementFromList('timed_led_1', 'led_min_off_timer')
                                    , self.setup.getConfigElementFromList('timed_led_1', 'led_max_off_timer')
                                    , self.setup.getConfigElementFromList('timed_led_1', 'led_check_timer')
                                    , self.setup.getConfigElementFromList('timed_led_1', 'always_on')
                                    , self.setup.getConfigElementFromList('timed_led_1', 'is_of_type')
                                    ))
        if self.setup.getConfigElementFromList('timed_led_2', 'PIN') != -1:
            logger.debug('init timed 2 light')
            self.timed_leds.append(led(self.setup
                                    , self.setup.getConfigElementFromList('timed_led_2', 'PIN')
                                    , self.setup.getConfigElementFromList('timed_led_2', 'NAME')
                                    , self.setup.getConfigElementFromList('timed_led_2', 'led_min_on_timer')
                                    , self.setup.getConfigElementFromList('timed_led_2', 'led_max_on_timer')
                                    , self.setup.getConfigElementFromList('timed_led_2', 'led_min_off_timer')
                                    , self.setup.getConfigElementFromList('timed_led_2', 'led_max_off_timer')
                                    , self.setup.getConfigElementFromList('timed_led_2', 'led_check_timer')
                                    , self.setup.getConfigElementFromList('timed_led_2', 'always_on')
                                    , self.setup.getConfigElementFromList('timed_led_2', 'is_of_type')
                                    ))
        if self.setup.getConfigElementFromList('timed_led_3', 'PIN') != -1:
            logger.debug('init timed 3 light')
            self.timed_leds.append(led(self.setup
                                    , self.setup.getConfigElementFromList('timed_led_3', 'PIN')
                                    , self.setup.getConfigElementFromList('timed_led_3', 'NAME')
                                    , self.setup.getConfigElementFromList('timed_led_3', 'led_min_on_timer')
                                    , self.setup.getConfigElementFromList('timed_led_3', 'led_max_on_timer')
                                    , self.setup.getConfigElementFromList('timed_led_3', 'led_min_off_timer')
                                    , self.setup.getConfigElementFromList('timed_led_3', 'led_max_off_timer')
                                    , self.setup.getConfigElementFromList('timed_led_3', 'led_check_timer')
                                    , self.setup.getConfigElementFromList('timed_led_3', 'always_on')
                                    , self.setup.getConfigElementFromList('timed_led_3', 'is_of_type')
                                    ))
        if self.setup.getConfigElementFromList('timed_led_4', 'PIN') != -1:
            logger.debug('init timed 4 light')
            self.timed_leds.append(led(self.setup
                                    , self.setup.getConfigElementFromList('timed_led_4', 'PIN')
                                    , self.setup.getConfigElementFromList('timed_led_4', 'NAME')
                                    , self.setup.getConfigElementFromList('timed_led_4', 'led_min_on_timer')
                                    , self.setup.getConfigElementFromList('timed_led_4', 'led_max_on_timer')
                                    , self.setup.getConfigElementFromList('timed_led_4', 'led_min_off_timer')
                                    , self.setup.getConfigElementFromList('timed_led_4', 'led_max_off_timer')
                                    , self.setup.getConfigElementFromList('timed_led_4', 'led_check_timer')
                                    , self.setup.getConfigElementFromList('timed_led_4', 'always_on')
                                    , self.setup.getConfigElementFromList('timed_led_4', 'is_of_type')
                                    ))
        
        #
        #   THE FLICKER LIGHTS
        #
        if self.setup.getConfigElementFromList('flicker_led_1', 'PIN') != -1:
            logger.debug('init flicker 1 light')
            self.flicker_leds.append(led(self.setup
                                    , self.setup.getConfigElementFromList('flicker_led_1', 'PIN')
                                    , self.setup.getConfigElementFromList('flicker_led_1', 'NAME')
                                    , self.setup.getConfigElementFromList('flicker_led_1', 'led_min_on_timer')
                                    , self.setup.getConfigElementFromList('flicker_led_1', 'led_max_on_timer')
                                    , self.setup.getConfigElementFromList('flicker_led_1', 'led_min_off_timer')
                                    , self.setup.getConfigElementFromList('flicker_led_1', 'led_max_off_timer')
                                    , self.setup.getConfigElementFromList('flicker_led_1', 'led_check_timer')
                                    , self.setup.getConfigElementFromList('flicker_led_1', 'always_on')
                                    , self.setup.getConfigElementFromList('flicker_led_1', 'is_of_type')
                                    ))
        if self.setup.getConfigElementFromList('flicker_led_2', 'PIN') != -1:
            logger.debug('init flicker 2 light')
            self.flicker_leds.append(led(self.setup
                                    , self.setup.getConfigElementFromList('flicker_led_2', 'PIN')
                                    , self.setup.getConfigElementFromList('flicker_led_2', 'NAME')
                                    , self.setup.getConfigElementFromList('flicker_led_2', 'led_min_on_timer')
                                    , self.setup.getConfigElementFromList('flicker_led_2', 'led_max_on_timer')
                                    , self.setup.getConfigElementFromList('flicker_led_2', 'led_min_off_timer')
                                    , self.setup.getConfigElementFromList('flicker_led_2', 'led_max_off_timer')
                                    , self.setup.getConfigElementFromList('flicker_led_2', 'led_check_timer')
                                    , self.setup.getConfigElementFromList('flicker_led_2', 'always_on')
                                    , self.setup.getConfigElementFromList('flicker_led_2', 'is_of_type')
                                    ))
        if self.setup.getConfigElementFromList('flicker_led_3', 'PIN') != -1:
            logger.debug('init flicker 3 light')
            self.flicker_leds.append(led(self.setup
                                    , self.setup.getConfigElementFromList('flicker_led_3', 'PIN')
                                    , self.setup.getConfigElementFromList('flicker_led_3', 'NAME')
                                    , self.setup.getConfigElementFromList('flicker_led_3', 'led_min_on_timer')
                                    , self.setup.getConfigElementFromList('flicker_led_3', 'led_max_on_timer')
                                    , self.setup.getConfigElementFromList('flicker_led_3', 'led_min_off_timer')
                                    , self.setup.getConfigElementFromList('flicker_led_3', 'led_max_off_timer')
                                    , self.setup.getConfigElementFromList('flicker_led_3', 'led_check_timer')
                                    , self.setup.getConfigElementFromList('flicker_led_3', 'always_on')
                                    , self.setup.getConfigElementFromList('flicker_led_3', 'is_of_type')
                                    ))
        if self.setup.getConfigElementFromList('flicker_led_4', 'PIN') != -1:
            logger.debug('init flicker 4 light')
            self.flicker_leds.append(led(self.setup
                                    , self.setup.getConfigElementFromList('flicker_led_4', 'PIN')
                                    , self.setup.getConfigElementFromList('flicker_led_4', 'NAME')
                                    , self.setup.getConfigElementFromList('flicker_led_4', 'led_min_on_timer')
                                    , self.setup.getConfigElementFromList('flicker_led_4', 'led_max_on_timer')
                                    , self.setup.getConfigElementFromList('flicker_led_4', 'led_min_off_timer')
                                    , self.setup.getConfigElementFromList('flicker_led_4', 'led_max_off_timer')
                                    , self.setup.getConfigElementFromList('flicker_led_4', 'led_check_timer')
                                    , self.setup.getConfigElementFromList('flicker_led_4', 'always_on')
                                    , self.setup.getConfigElementFromList('flicker_led_4', 'is_of_type')
                                    ))
        if self.setup.getConfigElementFromList('flicker_led_5', 'PIN') != -1:
            logger.debug('init flicker 5 light')
            self.flicker_leds.append(led(self.setup
                                    , self.setup.getConfigElementFromList('flicker_led_5', 'PIN')
                                    , self.setup.getConfigElementFromList('flicker_led_5', 'NAME')
                                    , self.setup.getConfigElementFromList('flicker_led_5', 'led_min_on_timer')
                                    , self.setup.getConfigElementFromList('flicker_led_5', 'led_max_on_timer')
                                    , self.setup.getConfigElementFromList('flicker_led_5', 'led_min_off_timer')
                                    , self.setup.getConfigElementFromList('flicker_led_5', 'led_max_off_timer')
                                    , self.setup.getConfigElementFromList('flicker_led_5', 'led_check_timer')
                                    , self.setup.getConfigElementFromList('flicker_led_5', 'always_on')
                                    , self.setup.getConfigElementFromList('flicker_led_5', 'is_of_type')
                                    ))
        #
        #   THE FADER LIGHTS
        #
        if self.setup.getConfigElementFromList('fader_led_1', 'PIN') != -1:
            logger.debug('init fader 1 light')
            self.fader_leds.append(led(self.setup
                                    , self.setup.getConfigElementFromList('fader_led_1', 'PIN')
                                    , self.setup.getConfigElementFromList('fader_led_1', 'NAME')
                                    , self.setup.getConfigElementFromList('fader_led_1', 'led_min_on_timer')
                                    , self.setup.getConfigElementFromList('fader_led_1', 'led_max_on_timer')
                                    , self.setup.getConfigElementFromList('fader_led_1', 'led_min_off_timer')
                                    , self.setup.getConfigElementFromList('fader_led_1', 'led_max_off_timer')
                                    , self.setup.getConfigElementFromList('fader_led_1', 'led_check_timer')
                                    , self.setup.getConfigElementFromList('fader_led_1', 'always_on')
                                    , self.setup.getConfigElementFromList('fader_led_1', 'is_of_type')
                                    ))
        if self.setup.getConfigElementFromList('fader_led_2', 'PIN') != -1:
            logger.debug('init fader 2 light')
            self.fader_leds.append(led(self.setup
                                    , self.setup.getConfigElementFromList('fader_led_2', 'PIN')
                                    , self.setup.getConfigElementFromList('fader_led_2', 'NAME')
                                    , self.setup.getConfigElementFromList('fader_led_2', 'led_min_on_timer')
                                    , self.setup.getConfigElementFromList('fader_led_2', 'led_max_on_timer')
                                    , self.setup.getConfigElementFromList('fader_led_2', 'led_min_off_timer')
                                    , self.setup.getConfigElementFromList('fader_led_2', 'led_max_off_timer')
                                    , self.setup.getConfigElementFromList('fader_led_2', 'led_check_timer')
                                    , self.setup.getConfigElementFromList('fader_led_2', 'always_on')
                                    , self.setup.getConfigElementFromList('fader_led_2', 'is_of_type')
                                    ))
        if self.setup.getConfigElementFromList('fader_led_3', 'PIN') != -1:
            logger.debug('init fader 3 light')
            self.fader_leds.append(led(self.setup
                                    , self.setup.getConfigElementFromList('fader_led_3', 'PIN')
                                    , self.setup.getConfigElementFromList('fader_led_3', 'NAME')
                                    , self.setup.getConfigElementFromList('fader_led_3', 'led_min_on_timer')
                                    , self.setup.getConfigElementFromList('fader_led_3', 'led_max_on_timer')
                                    , self.setup.getConfigElementFromList('fader_led_3', 'led_min_off_timer')
                                    , self.setup.getConfigElementFromList('fader_led_3', 'led_max_off_timer')
                                    , self.setup.getConfigElementFromList('fader_led_3', 'led_check_timer')
                                    , self.setup.getConfigElementFromList('fader_led_3', 'always_on')
                                    , self.setup.getConfigElementFromList('fader_led_3', 'is_of_type')
                                    ))
        if self.setup.getConfigElementFromList('fader_led_4', 'PIN') != -1:
            logger.debug('init fader 4 light')
            self.fader_leds.append(led(self.setup
                                    , self.setup.getConfigElementFromList('fader_led_4', 'PIN')
                                    , self.setup.getConfigElementFromList('fader_led_4', 'NAME')
                                    , self.setup.getConfigElementFromList('fader_led_4', 'led_min_on_timer')
                                    , self.setup.getConfigElementFromList('fader_led_4', 'led_max_on_timer')
                                    , self.setup.getConfigElementFromList('fader_led_4', 'led_min_off_timer')
                                    , self.setup.getConfigElementFromList('fader_led_4', 'led_max_off_timer')
                                    , self.setup.getConfigElementFromList('fader_led_4', 'led_check_timer')
                                    , self.setup.getConfigElementFromList('fader_led_4', 'always_on')
                                    , self.setup.getConfigElementFromList('fader_led_4', 'is_of_type')
                                    ))
        if self.setup.getConfigElementFromList('fader_led_5', 'PIN') != -1:
            logger.debug('init fader 5 light')
            self.fader_leds.append(led(self.setup
                                    , self.setup.getConfigElementFromList('fader_led_5', 'PIN')
                                    , self.setup.getConfigElementFromList('fader_led_5', 'NAME')
                                    , self.setup.getConfigElementFromList('fader_led_5', 'led_min_on_timer')
                                    , self.setup.getConfigElementFromList('fader_led_5', 'led_max_on_timer')
                                    , self.setup.getConfigElementFromList('fader_led_5', 'led_min_off_timer')
                                    , self.setup.getConfigElementFromList('fader_led_5', 'led_max_off_timer')
                                    , self.setup.getConfigElementFromList('fader_led_5', 'led_check_timer')
                                    , self.setup.getConfigElementFromList('fader_led_5', 'always_on')
                                    , self.setup.getConfigElementFromList('fader_led_5', 'is_of_type')
                                    ))
    
    def turnOffAllLights(self):
        # cancel the background tasks of the timed lights
        if len(self.timed_leds) > 0:
            logger.trace('powering off the timed lights')
            self.poweroff('timed')
        
        # cancel the background tasks of the flicker lights
        if len(self.flicker_leds) > 0:
            logger.trace('powering off the flicker lights')
            self.poweroff('flicker')
        
        # cancel the background tasks of the fader lights
        if len(self.fader_leds) > 0:
            logger.trace('powering off the fader lights')
            self.poweroff('fader')
        
        # turn off standard lights except the always on lights
        if len(self.standard_leds) > 0:
            logger.trace('powering off the standard lights')
            self.poweroff('standard', True)
        
    #
    #   OPERATE THE LIGHTS
    #
    def getActiveLights(self, name_of_lights):
        array_of_lights = []
        if name_of_lights == 'flicker':
            array_of_lights = self.flicker_leds
        elif name_of_lights == 'fader':
            array_of_lights = self.fader_leds
        elif name_of_lights == 'timed':
            array_of_lights = self.timed_leds
        elif name_of_lights == 'standard':
            array_of_lights = self.standard_leds
        if len(array_of_lights) > 0:
            return(True)
        return(False)
    
    #
    #   LOW LEVEL DRIVER FUNCTIONS
    #
    def poweron(self, name_of_lights):
        if name_of_lights == 'standard':
            array_of_lights = self.standard_leds
        elif name_of_lights == 'flicker':
            array_of_lights = self.flicker_leds
        elif name_of_lights == 'fader':
            array_of_lights = self.fader_leds
        elif name_of_lights == 'timed':
            array_of_lights = self.timed_leds
        else:
            return(False)
        
        if name_of_lights == 'standard':
            if len(self.standard_leds) > 0:
                logger.debug('turn on standard lights')
                for element in array_of_lights:
                    element.poweron()
        else:
            if len(array_of_lights) > 0 and array_of_lights[0].bg_task_active == False:
                logger.debug('initiating bg task for '+name_of_lights+' leds')
                for element in array_of_lights:
                    element.poweron()
    
    def poweroff(self, name_of_lights, all_lights=False):
        if name_of_lights == 'standard':
            array_of_lights = self.standard_leds
        elif name_of_lights == 'flicker':
            array_of_lights = self.flicker_leds
        elif name_of_lights == 'fader':
            array_of_lights = self.fader_leds
        elif name_of_lights == 'timed':
            array_of_lights = self.timed_leds
        else:
            return(False)
        
        if name_of_lights == 'standard':
            if len(self.standard_leds) > 0:
                logger.debug('turn off standard lights')
                for element in self.standard_leds:
                    if element.always_on == False or all_lights == True:
                        element.poweroff()
        else:
            if len(array_of_lights) > 0:
                logger.debug('cancelling bg task for '+name_of_lights+' leds')        
                for element in array_of_lights:
                    logger.trace('powering off ' + str(element))
                    element.poweroff()
    
    def getStatus(self, lights):
        ret_code = 0
        if lights == 'flicker' and len(self.flicker_leds) > 0:
            ret_code = self.flicker_leds[0].getStatus()
        elif lights == 'fader' and len(self.fader_leds) > 0:
            ret_code = self.fader_leds[0].getStatus()
        elif lights == 'timed' and len(self.timed_leds) > 0:
            ret_code = self.timed_leds[0].getStatus()
        elif lights == 'standard' and len(self.standard_leds) > 0:
            ret_code = self.standard_leds[0].getStatus()
        logger.trace('returning ' + str(ret_code) + ' as state for ' + str(lights))
        return(ret_code)
    