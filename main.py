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
#    MAIN LOOP                                               #
# ---------------------------------------------------------- #
# initializes all the classes and starts the main check      #
# and run loop in the background                             #
#                                                            #
# ---------------------------------------------------------- #
# V1.0 01.11.2022 initial release                            #
# V1.1 30.10.2023 minor changes to exception handling        #
##############################################################

#
import time
import uasyncio as asyncio
from logging import getLogger
logger = getLogger(__name__)
# SEVERITY = CRITICAL ERROR WARNING INFO DEBUG TRACE CRAZY
logger.setLevel('INFO')

# source in and initialize all the classes of the individual parts of the
# diorama
from setup import setup
from clock import clock
from motion import motion
from lights import lights
from display import display
from door import door
from checkandrun import checkandrun
my_setup = setup()
my_clock = clock(my_setup)
my_motion = motion(my_setup)
my_lights = lights(my_setup)
my_display = display(my_setup, my_clock)
if my_setup.getConfigParameter('use_door') == True:
    my_door = door(my_setup)
else:
    my_door = ''

# with the initialized classes of the individual components we now initialize the
# main check-and-run class passing all class objects along. This is done, so that
# the check and run class con operate the individual parts of the diorama - it may
# also be possible to do this from within the check and run class itself, but I
# prefer it in this way, where  pass the class objects. Additionally, if I do it
# here, I can turn off everything from within the main loop, when the program is
# interupted or terminates
my_checkandrun = checkandrun(my_setup, my_clock, my_motion, my_display, my_door, my_lights)


def main():
    ON = my_setup.getConfigParameter('ON')
    OFF = my_setup.getConfigParameter('OFF')
    
    sleep_counter = 0
    
    max_counter_for_short_sleep = my_setup.getConfigParameter('max_counter_for_5_s_sleep')   # 12
    no_active_hours_short_sleep_between_checks_in_ms = my_setup.getConfigParameter('no_active_hours_short_sleep_between_checks_in_ms')
    no_active_hours_long_sleep_between_checks_in_ms  = my_setup.getConfigParameter('no_active_hours_long_sleep_between_checks_in_ms')
    
    try:
        logger.info('')
        logger.info('######         Starting up - to cancel hit Ctrl+C        ######')
        logger.info('')
        while True:
            
            asyncio.run(my_checkandrun.checkAndRun())
                
            ##################################################################
            ####                                                          ####
            ####     IN CASE WE ARE NOT WITHIN THE ACTIVE HOURSE TURN     ####
            ####     EVERYTHING OFF and SLEEP A BIT BEFOR TRYING AGAIN    ####
            ####                                                          ####
            ##################################################################
            # cancel the background tasks of the flicker, fader or timed lights
            # turn off all standard lights
            my_lights.turnOffAllLights()
                
            # only in case the video is still on, turn it off
            if my_display.getStatus() == ON:
                my_display.poweroff()
            
            if sleep_counter == max_counter_for_short_sleep:
                logger.info('Sleeping 5 minutes - to finally cancel hit Ctrl+C')
                time.sleep_ms(no_active_hours_long_sleep_between_checks_in_ms)
                sleep_counter = 0
            else:
                logger.info('Sleeping 5 seconds - to finally cancel hit Ctrl+C')
                time.sleep_ms(no_active_hours_short_sleep_between_checks_in_ms)
                sleep_counter += 1
    except KeyboardInterrupt:
        # cancel the background tasks of the flicker, fader or timed lights
        # turn off all standard lights
        my_lights.turnOffAllLights()
        # only in case the video is still on, turn it off
        if my_display.getStatus() == ON:
            my_display.poweroff()
        
        logger.info('Interrupted')
        logger.info('######                        END                        ######')
        logger.info('')
    except Exception as e:
        # cancel the background tasks of the flicker, fader or timed lights
        # turn off all standard lights
        my_lights.turnOffAllLights()
        # only in case the video is still on, turn it off
        if my_display.getStatus() == ON:
            my_display.poweroff()
        
        logger.error('Error: ' + str(e))

if __name__ == '__main__':
    main()

