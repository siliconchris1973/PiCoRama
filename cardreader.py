from machine import Pin, SPI
import os

import sdcard_rp2 as sdcard

from logging import getLogger
logger = getLogger(__name__)
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
    