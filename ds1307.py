# License-Identifier: MIT

"""
DS1307 Real Time Clock driver
=============================

MicroPython library to support DS1307 Real Time Clock (RTC).

Acknowledgement: This module was derived in outline from the adafruit circuit python DS1307
real time clock library. That library was authored by Philip R. Moyer and
Radomir Dopieralski for Adafruit Industries.
See repository: https://github.com/adafruit/Adafruit_CircuitPython_DS1307.git

Beware the DS1307 breakout is a 5V board but many boards are 3.3v logic level!
Make sure that the SCL and SDA pins used are 5v tolerant or level shifted to 3.3v.

* Author: Peter Lumb (@peter-l5)
* Build: v104

Implementation Notes
--------------------

**Hardware:**

* For example: Adafruit `DS1307 RTC breakout <https://www.adafruit.com/products/3296>`
  (Adafruit Product ID: 3296)

**Software and Dependencies:**

* micropython firmware: https://micropython.org/

**Notes:**

#1.  the square-wave output facility is not supported by this driver.
#2.  milliseconds are not supported by this RTC.
#3.  alarms and timers are not supported by this RTC.
#4.  datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/ds1307.pdf

"""

__version__ = "v104"
__repo__ = "https://github.com/peter-l5"

from micropython import const

# register definitions (see datasheet)
_DATETIME_REGISTER = const(0x00)
_CONTROL_REGISTER  = const(0x07)

class DS1307():
    """
    Interface to the DS1307 RTC.

    **Quickstart: Importing and using the device**

        Here is an example of using the :class:`DS1307` class.
        First you will need to import the libraries to use the sensor

        .. code-block:: python

            from machine import Pin, SoftI2C
            import ds1307

        Once this is done you can define your `board.I2C` object and define your DS1307 clock object

        .. code-block:: python

            # uses SoftI2C class and pins for Raspberry Pi pico 
            i2c0 = SoftI2C(scl=Pin(1), sda=Pin(0), freq=100000)
            ds1307rtc = ds1307.DS1307(i2c0, 0x68)

        Now you can give the current time to the device.

        .. code-block:: python

            # set time (year, month, day, hours. minutes, seconds, weekday: integer: 0-6 )
            ds1307rtc.datetime = (2022, 12, 18, 18, 9, 17, 6)

        You can access the current time with the :attr:`datetime` property.

        .. code-block:: python

            current_time = ds1307rtc.datetime

        You can also access the current time with the :attr:`datetimeRTC` property.
        This returns the time in a format suitable for directly setting the internal RTC clock
        of the Raspberry Pi Pico (once the RTC module is imported).

        .. code-block:: python

        from machine import RTC
        machine.RTC().datetime(ds1307rtc.datetimeRTC)

        The disable oscillator property may be useful to stop the clock when not in use
        to reduce demand on the standby battery.
        
        See also the example code provided.
    """

    def __init__(self, i2c_bus: I2C, addr = 0x68) -> None:
        self.i2c = i2c_bus
        self.addr = addr
        self.buf = bytearray(7)
        self.buf1 = bytearray(1)

    @property
    def datetime(self) -> tuple:
        """Returns the current date, time and day of the week."""
        self.i2c.readfrom_mem_into(self.addr, _DATETIME_REGISTER, self.buf)
        hr24 = False if (self.buf[2] & 0x40) else True
        _datetime = (self._bcd2dec(self.buf[6]) + 2000,
                     self._bcd2dec(self.buf[5]),
                     self._bcd2dec(self.buf[4]),
                     self._bcd2dec(self.buf[2]) if hr24 else
                         self._bcd2dec((self.buf[2] & 0x1f))
                         +  12 if (self.buf[2] & 0x20) else 0,
                     self._bcd2dec(self.buf[1]), # minutes
                     self._bcd2dec(self.buf[0] & 0x7f), # seconds, remove oscilator disable flag
                     self.buf[3] -1,
                     None # unknown number of days since start of year
                     )
        return _datetime        

    @datetime.setter
    def datetime(self, datetime: tuple = None):
        """Set the current date, time and day of the week, and starts the clock."""
        self.buf[6] = self._dec2bcd(datetime[0] % 100) # years
        self.buf[5] = self._dec2bcd(datetime[1] ) # months
        self.buf[4] = self._dec2bcd(datetime[2] ) # days
        self.buf[2] = self._dec2bcd(datetime[3] ) # hours
        self.buf[1] = self._dec2bcd(datetime[4] ) # minutes
        self.buf[0] = self._dec2bcd(datetime[5] ) # seconds
        self.buf[3] = self._dec2bcd(datetime[6] +1) # weekday (0-6)
        self.i2c.writeto_mem(self.addr, _DATETIME_REGISTER, self.buf)
 
    @property
    def datetimeRTC(self) -> tuple:
        _dt = self.datetime
        return _dt[0:3] + (None,) + _dt[3:6] + (None,)
 
    @property
    def disable_oscillator(self) -> bool:
        """True if the oscillator is disabled."""
        self.i2c.readfrom_mem_into(self.addr, _DATETIME_REGISTER, self.buf1)
        self._disable_oscillator = bool(self.buf1[0] & 0x80)
        return self._disable_oscillator
    
    @disable_oscillator.setter
    def disable_oscillator(self, value: bool):
        """Set or clear the DS1307 disable oscillator flag."""
        self._disable_oscillator = value
        self.i2c.readfrom_mem_into(self.addr, _DATETIME_REGISTER, self.buf1)
        self.buf1[0] &= 0x7f  # preserve seconds
        self.buf1[0] |= self._disable_oscillator << 7
        self.i2c.writeto_mem(self.addr, _DATETIME_REGISTER, self.buf1)
  
    def _bcd2dec(self, bcd):
        """Convert binary-coded decimal to decimal. Works for values from 0 to 99 (decimal)."""
        return (bcd >> 4) * 10 + (bcd & 0x0F)
    
    def _dec2bcd(self, decimal):
        """Convert decimal to binary-coded decimal. Works for values from 0 to 99."""
        return ((decimal // 10) << 4) + (decimal % 10)
  