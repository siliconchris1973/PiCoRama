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
# CHECK AND RUN                                              #
# ---------------------------------------------------------- #
# this is the check and run loop which periodically checks   #
# if there is motion (check done in the background from      #
# within the motion class) and then starts a show through    #
# the display class. Additionally this check and run loop    #
# would light up the leds (using lights and led class) and   #
# open/close the door (via door class)                       #
#                                                            #
# ---------------------------------------------------------- #
# V1.0 01.11.2022 initial release                            #
# V1.1 30.10.2023 added exception handling                   #
##############################################################
import time
import uasyncio as asyncio
from logging import getLogger
logger = getLogger(__name__)
# SEVERITY = CRITICAL ERROR WARNING INFO DEBUG TRACE CRAZY
logger.setLevel('DEBUG')

class checkandrun:
    ON = 1
    OFF = 0
    
    def __init__(self, setup, clock, motion, display, door, lights):
        logger.info('init checkandrun class')
        
        self.setup = setup
        
        self.ON = setup.getConfigParameter('ON')
        self.OFF = setup.getConfigParameter('OFF')

        self.my_clock = clock
        self.my_motion = motion
        self.my_display = display
        self.my_door = door
        self.my_lights = lights
        
        self.countdown_last_check_diff = self.setup.getConfigParameter('countdown_last_check_diff')
        
        self.sleep_between_checks_in_ms = self.setup.getConfigParameter('sleep_between_checks_in_ms')
        self.sleep_after_show_in_ms = self.setup.getConfigParameter('sleep_after_show_in_ms')
        self.show_date_and_time_show = self.setup.getConfigParameter('show_date_and_time_show')
        
        self.use_flicker_lights = self.my_lights.getActiveLights('flicker')
        self.use_fader_lights = self.my_lights.getActiveLights('fader')
        self.use_timed_lights = self.my_lights.getActiveLights('timed')
        self.use_standard_lights = self.my_lights.getActiveLights('standard')
        
        self.use_door = self.setup.getConfigParameter('use_door')
        self.door_last_check_diff = self.setup.getConfigParameter('door_last_check_diff')
        self.keep_door_closed_for = self.setup.getConfigParameter('keep_door_closed_for')
        self.keep_door_opened_for = self.setup.getConfigParameter('keep_door_opened_for')
        
        self.use_active_hours = self.setup.getConfigParameter('use_active_hours')
        self.sync_door_with_shows = self.setup.getConfigParameter('sync_door_with_shows')
        
        if self.use_active_hours == True:
            self.active_hours = self.setup.getConfigElementFromList('active_at', self.my_clock.getWeekday())
        else:
            self.active_hours = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
        
    ##################################################################
    ####                                                          ####
    ####                     CHECK DOOR STATE                     ####
    ####                                                          ####
    ##################################################################
    def checkDoorState(self, now_time, current_door_state_since, keep_door_closed_for, keep_door_opened_for):
        if self.use_door == True:
            cur_state = self.my_door.getStatus()
            if cur_state == self.OFF:
                status_change_at = current_door_state_since + keep_door_closed_for
            else:
                status_change_at = current_door_state_since + keep_door_opened_for
            
            if now_time >= status_change_at:
                logger.debug('door is '
                          + self.my_door.getStatusName(True)
                          + ' since '
                          + str(current_door_state_since)
                          + ' now is '
                          + str(now_time)
                          + ' state change at '
                          + str(status_change_at)
                          + ' => '
                          + self.my_door.getStatusName(False))
                current_door_state_since = now_time
                self.my_door.toggle()
            else:
                logger.debug('no need to change door state - door is '
                          + self.my_door.getStatusName(True)
                          + ' since '
                          + str(current_door_state_since)
                          + ' now is '
                          + str(now_time)
                          + ' next change at '
                          + str(status_change_at)
                          )
            return(current_door_state_since)
    
    
    ##################################################################
    ####                                                          ####
    ####                       CHECK AND RUN                      ####
    ####                                                          ####
    ##################################################################
    async def checkAndRun(self):
        start_time = 0
        count_down_last_display_time = 0
        
        try:
            there_is_motion = False
            
            while self.my_clock.getDateTimeElements('h') in self.active_hours:
                logger.trace('within active run time')
                ##################################################################
                ####                                                          ####
                ####                     TURN ON THE OLED                     ####
                ####                             &                            ####
                ####                    ANIMATE THE LIGHTS                    ####
                ####                                                          ####
                ##################################################################
                # initiate the background tasks for the flicker lights
                if self.use_flicker_lights == True and self.my_lights.getStatus('flicker') == self.OFF:
                    logger.debug('turn on flicker lights')
                    asyncio.run(self.my_lights.poweron('flicker'))
                
                # initiate the background tasks for the fader lights
                if self.use_fader_lights == True and self.my_lights.getStatus('fader') == self.OFF:
                    logger.debug('turn on fader lights')
                    asyncio.run(self.my_lights.poweron('fader'))
                
                # make sure the other lights are on as well
                if self.use_timed_lights == True and self.my_lights.getStatus('timed') == self.OFF:
                    logger.debug('turn on timed lights')
                    asyncio.run(self.my_lights.poweron('timed'))
                
                # make sure the other lights are on as well
                if self.use_standard_lights == True and self.my_lights.getStatus('standard') == self.OFF:
                    logger.debug('turn on standard lights')
                    self.my_lights.poweron('standard')
                
                ##################################################################
                ####                                                          ####
                ####        CHECK DOOR STATE AND EITHER OPEN OR CLOSE IT      ####
                ####                                                          ####
                ##################################################################
                if self.use_door == True:
                    if self.sync_door_with_shows == True:
                        logger.trace('checking door state')
                        current_door_state_since = time.ticks_ms()
                        door_last_check_time = 0
                        
                        now_time = time.ticks_ms()
                        if now_time > door_last_check_time + self.door_last_check_diff:
                            logger.trace('changing door state')
                            door_last_check_time = now_time
                            current_door_state_since = self.checkDoorState(now_time,
                                                                       current_door_state_since,
                                                                       self.keep_door_closed_for,
                                                                       self.keep_door_opened_for)
                
                ##################################################################
                ####                                                          ####
                ####           SHOW CURRENT TIME AND THE COUNTDOWN            ####
                ####                                                          ####
                ##################################################################
                if self.show_date_and_time_show == True:
                    logger.trace('showing time and date')
                    if time.ticks_ms() > count_down_last_display_time + self.countdown_last_check_diff and there_is_motion == False: # 60000 = 1 MInute
                        logger.debug('showing date and time and countdown')
                        count_down_last_display_time = time.ticks_ms()
                        
                        self.my_display.fillScreen(self.OFF)
                        hrs, mins, day, month, year = self.my_clock.getDateTimeElements('all')
                        text = [
                                str(hrs) + ':' + str(mins) + ' Uhr'
                                , str(day)+'.'+str(month)+'.'+str(year)
                                , 'noch ' + str(self.my_clock.remaining_days) + ' Tage']
                        
                        logger.trace('Uhrzeit aktualisiert um ' + str(count_down_last_display_time) + ': ' + str(text))
                        self.my_display.poweron()
                        asyncio.run(self.my_display.showText(text, True, True, 0, 0))
                        asyncio.run(self.waitABit(1)) #await asyncio.sleep_ms(1)
                
                ##################################################################
                ####                                                          ####
                ####                     CHECK FOR MOTION                     ####
                ####                                                          ####
                ##################################################################
                there_is_motion = self.my_motion.getMotion()
                if there_is_motion == True:
                    logger.debug('motion detected')
                    start_time = time.ticks_ms()
                    
                    if self.my_display.getStatus() == self.OFF:
                        logger.debug('power on display')
                        self.my_display.poweron()
                    self.my_display.fillScreen(0)
                    
                    if self.use_door == True:
                        logger.debug('opening the door')
                        self.my_door.poweron()
                
                ##################################################################
                ####                                                          ####
                ####           THIS IS THE PART WHEN A SHOW IS RUN            ####
                ####                                                          ####
                ##################################################################
                # check motion either returns a motion or True if ever so long nothing was shown
                while there_is_motion == True:
                    logger.trace('motion detected - run the show')
                    if self.use_door == True and self.sync_door_with_shows == False:
                        #
                        #   CHECK DOOR STATE AND EITHER OPEN OR CLOSE IT
                        #
                        now_time = time.ticks_ms()
                        if now_time > door_last_check_time + 60000:
                            door_last_check_time = now_time
                            current_door_state_since = self.checkDoorState(now_time,
                                                                       current_door_state_since,
                                                                       keep_door_closed_for,
                                                                       keep_door_opened_for)
                    #
                    # Show images and text on the display
                    # what and when is determined by the display class itself
                    #
                    logger.crazy('running a new show')
                    
                    show = []
                    the_shows = self.my_display.createTheShow()
                    logger.debug('these are the shows to run: ' + str(the_shows))
                    
                    self.my_display.poweron()
                    for show in the_shows:
                        logger.crazy('now running ' + str(show[0]) + ' from ' + str(show[1]))
                        self.my_display.displayTheShow(show)
                    self.my_display.blankScreen()
                    #self.my_display.poweroff()
                    
                    logger.trace(str(time.ticks_ms()) + ' show done sleeping for ' + str(self.sleep_after_show_in_ms) + ' ms')
                    asyncio.run(self.waitABit(self.sleep_after_show_in_ms))
                    logger.trace(str(time.ticks_ms()) + ' waiting done - now checking for new motion')
                    
                    there_is_motion = self.my_motion.getMotion()
                    if there_is_motion == False:
                        self.my_display.blankScreen()
                        self.my_display.poweroff()
                        if self.use_door == True:
                            logger.debug('closing the door')
                            self.my_door.poweroff()
                            
                ##################################################################
                ####                                                          ####
                ####                      THE SHOW IS OVER                    ####
                ####                                                          ####
                ##################################################################
                # turn off standard lights except the always on lights
                if self.use_standard_lights == True and self.my_lights.getStatus('standard') == self.ON:
                    logger.debug('turn off standard lights')
                    self.my_lights.poweroff('standard')                
                # finally wait 
                asyncio.run(self.waitABit(self.sleep_between_checks_in_ms))
                
            ##################################################################
            ####                                                          ####
            ####      IN CASE WE ARE NOT WITHIN THE ACTIVE HOURSE         ####
            ####              TURN EVERYTHING OFF and EXIT                ####
            ####                                                          ####
            ##################################################################
            logger.info(str(self.my_clock.getDateTimeElements('h'))
                      + ' hours on '
                      + str(self.my_clock.getWeekday())
                      + ' is an inactive time - exiting' )
            
            self.my_lights.turnOffAllLights()
            
            # only in case the video is still on, turn it off
            if self.my_display.getStatus() == self.ON:
                logger.trace('power off display')
                self.my_display.poweroff()
            logger.debug('ran for '+str(time.ticks_diff(time.ticks_ms(), start_time)) + ' exiting')
        
        except KeyboardInterrupt:
            logger.warning('Interrupted - Display and Lights off')
            if self.use_door == True:
                self.my_door.poweroff()
            self.my_display.fillScreen(self.OFF)
            self.my_display.poweroff()
            self.my_lights.turnOffAllLights()
            
        except MemoryError:
            logger.critical('Memory exhausted - Display and Lights off')
            if self.use_door == True:
                self.my_door.poweroff()
            self.my_display.fillScreen(self.OFF)
            self.my_display.poweroff()
            self.my_lights.turnOffAllLights()
        
        #except Exception as e:
        #    logger.critical('Error in check and run loop: ' +str(e))
        #    if self.use_door == True:
        #        self.my_door.poweroff()
        #    self.my_display.fillScreen(self.OFF)
        #    self.my_display.poweroff()
        #    self.my_lights.turnOffAllLights()
        
    async def waitABit(self, milliseconds=1):
        await asyncio.sleep_ms(milliseconds)
    