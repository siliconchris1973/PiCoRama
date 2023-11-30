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
# Version: 1.2                                               #
#                                                            #
##############################################################
#                                                            #
#   CLOCK                                                    #
# ---------------------------------------------------------- #
# provides time and date information                         #
# The class can make use of a RTC module and in that case    #
# will return realtime information on date and time. If      #
# the countdown to show dates until a specific date is       #
# used a hardware rtc is needed                              #
#                                                            #
#   to set the hw rtc:                                       #
#   from machine import Pin, SoftI2C                         #
#   import ds1307                                            #
#   i2c0 = SoftI2C(scl=Pin(21), sda=Pin(20), freq=100000)    #
#   ds1307rtc = ds1307.DS1307(i2c0, 0x68)                    #
#   ds1307rtc.datetime = (2023, 10, 28, 12, 11, 00, 6)       #
#                                                            #
# ---------------------------------------------------------- #
# V1.0 01.11.2022 initial release                            #
# V1.1 28.10.2023 updates necessary for the new ds1307.py    #
#                 low level driver                           #
# V1.2 30.10.2023 added exception handling to clock methods  #
##############################################################
from machine import Pin, I2C
import utime, time
import ds1307
from logging import getLogger
logger = getLogger(__name__)
# SEVERITY = CRITICAL ERROR WARNING INFO DEBUG TRACE CRAZY
logger.setLevel('INFO')

class clock:
    ON = 1
    OFF = 0
    
            # year month day weekday hour minute second
    cur_time = (2023, 10, 27, 5, 11, 11, 00)
    target_date = (2023, 12, 24, 5, 11, 11, 00)
    
    wait_till_next_check = 43200000 # 12 hours
        
    def __init__(self, setup):
        self.setup = setup
        
        local_i2c = self.setup.getConfigParameter('rtc_i2c')
        local_sda = self.setup.getConfigParameter('rtc_sda_pin')
        local_scl = self.setup.getConfigParameter('rtc_scl_pin')
        
        self.use_clock = self.setup.getConfigParameter('use_clock')
        self.target_date = self.setup.getConfigParameter('target_date')
        
        self.last_check_time = 0
        self.remaining_days = 0 # if the countdown is active these are the remaining days till the event
        
        # Initialisierung
        if self.use_clock == True:
            self.i2c = I2C(local_i2c, sda=Pin(local_sda), scl=Pin(local_scl))
            self.rtc = ds1307.DS1307(self.i2c)
        
        logger.info('init clock class')
        logger.debug(' i2c ' + str(local_i2c)
                        + ' sda pin ' + str(local_sda)
                        + ' scl pin ' + str(local_scl)
                      )
    
    def getDateTimeElements(self, element='h'):
        if self.use_clock == True:
            try:
                self.cur_time = self.rtc.datetime
            except Exception as e:
                logger.error('could not communicate with the real time clock: '+str(e))
        day = self.cur_time[2]
        month = self.cur_time[1]
        year = self.cur_time[0]
        hour = self.cur_time[3]
        minute = self.cur_time[4]
        
        logger.crazy('date time element queried at '
                     + str(hour) + ':' + str(minute) + ' '
                     + str(day) + '.' + str(month) + '.' + str(year)
                     )
            
        if element == 'h':
            return(hour)
        elif element == 'm':
            return(minute)
        elif element == 'd':
            return(day)
        elif element == 'M':
            return(month)
        elif element == 'y':
            return(year)
        else:
            return(hour, minute, day, month, year)
    
    def getWeekday(self):
        if self.use_clock == True:
            try:
                self.cur_time = self.rtc.datetime
            except Exception as e:
                logger.error('could not communicate with the real time clock: '+str(e))
        
        weekday = self.cur_time[6]
        logger.trace('current weekday ' + str(weekday) + '=' + self.setup.getConfigElementFromList('weekdays', weekday))
        
        return(self.setup.getConfigElementFromList('weekdays', weekday))
    
    def getDateTime(self):
        if self.use_clock == True:
            try:
                self.cur_time = self.rtc.datetime
            except Exception as e:
                logger.error('could not communicate with the real time clock: '+str(e))
        
        weekday=self.getWeekday()
        datum=str(self.cur_time[2]) +'.' + str(self.cur_time[1]) + '.' +str(self.cur_time[0])
        uhrzeit=str(self.cur_time[3]) +':' + str(self.cur_time[4]) + ':' +str(self.cur_time[5]) + ' Uhr'
        time_array = [weekday, datum, uhrzeit]
        return(time_array)
                
    def printTime(self):
        # Zeit lesen und ausgeben
        if self.use_clock == True:
            try:
                self.cur_time = self.rtc.datetime
            except Exception as e:
                logger.error('could not communicate with the real time clock: '+str(e))
        time_text = 'Es ist ' + self.getWeekday() + ', der ' + str(self.cur_time[2]) + '.' + str(self.cur_time[1]) + '.' +str(self.cur_time[0]) + ' ' + str(self.cur_time[3]) + ':' + str(self.cur_time[4]) + ':' +str(self.cur_time[5]) + ' Uhr'
        
        logger.info(time_text)
        print(time_text)
                
    
    def countdown(self):
        if time.ticks_ms() > self.last_check_time + self.wait_till_next_check:
            self.last_check_time = time.ticks.ms()
            
            def days_between(d1, d2):
                #d1 += (1, 0, 0, 0, 0)  # ensure a time past midnight
                #d2 += (1, 0, 0, 0, 0)
                return (utime.mktime(d1) // (24*3600)) - (utime.mktime(d2) // (24*3600))
            
            logger.debug('geting the time till countdown')
            
            if self.use_clock == True:
                try:
                    self.cur_time = self.rtc.datetime
                except Exception as e:
                    logger.error('could not communicate with the real time clock: '+str(e))
            cur_d = self.cur_time[2]
            cur_m = self.cur_time[1]
            cur_y = self.cur_time[0]
            
            tar_d = self.target_date[2]
            tar_m = self.target_date[1]
            tar_y = self.target_date[0]
            
            date1 = (tar_y, tar_m, tar_d)
            date2 = (cur_y, cur_m, cur_d)
            self.remaining_days = days_between(date1, date2)
            
            logger.debug(' current date '
                         + str(cur_d) + '.'
                         + str(cur_m) + '.'
                         + str(cur_y)
                         + ' target date '
                         + str(tar_d) + '.'
                         + str(tar_m) + '.'
                         + str(tar_y)
                         + ' remaining days '
                         + str(self.remaining_days)
                         )
            
        return(self.remaining_days)
    
    def setTime(year, month, day, weekday, hour, minute, second):
        logger.info('setting date time to ' + str(day) + '.' + str(month) + '.' + str(year) + ' ' + str(hour) + ':' + str(minute) + ':' + str(second))
        