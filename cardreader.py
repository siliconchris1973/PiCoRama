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
#    CARDREADER                                              #
# ---------------------------------------------------------- #
# High level driver for the card reader. Makes use of        #
# sdcard_rp2 to provide an interface for reading and writing #
# to an sd-card. Used to store and retrieve animations etc.  #
#                                                            #
# ---------------------------------------------------------- #
# V1.0 01.11.2022 initial release                            #
##############################################################
from machine import Pin, SPI
import os

import sdcard_rp2 as sdcard

from logging import getLogger
logger = getLogger(__name__)
# SEVERITY = CRITICAL ERROR WARNING INFO DEBUG TRACE CRAZY
logger.setLevel('TRACE')

class cardreader:
    ON = 1
    OFF = 0
    
    def __init__(self, setup):
        self.sdcard_sck = 10
        self.sdcard_mosi = 11
        self.sdcard_miso = 12
        self.sdcard_cs = 13
        
        self.setup = setup
        self.ON = self.setup.getConfigParameter('ON')
        self.OFF = self.setup.getConfigParameter('OFF')
        
        logger.info('init cardreader class')
        spi = SPI(1
                  , baudrate=1320000
                  , polarity=0
                  , phase=0
                  , bits=8
                  , firstbit=SPI.MSB
                  , sck=Pin(self.setup.getConfigParameter('sdcard_sck'))
                  , mosi=Pin(self.setup.getConfigParameter('sdcard_mosi'))
                  , miso=Pin(self.setup.getConfigParameter('sdcard_miso'))
                  )
        cs = Pin(self.setup.getConfigParameter('sdcard_cs'), Pin.OUT)
        
        logger.debug('SD card: spi='+str(spi)+' cs='+str(cs))
        self.sd = sdcard.SDCard(spi,cs)
        
        # Create a instance of MicroPython Unix-like Virtual File System (VFS),
        #logger.trace('creating VFS')
        #self.vfs=os.VfsFat(self.sd)
        
        logger.trace('SD Card has ' + str(self.sd.sectors) + ' sectors')
        # Mount the SD card
        logger.debug('mounting filesystem')
        os.umount("/")
        os.mount(self.sd,'/')
        os.listdir("/")
        
        logger.debug(str(os.listdir('/')))
    