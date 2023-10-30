##############################################################
# PiCoRama is a complete set of MicroPython scripts that can #
# handle a diorama - this diorama may contain various lights #
# some of which may be turn ed on / off at certain times,    #
# may flicker or fade. Additionally a motion detectore with  #
# a PIR can be used to initialize tv shows on a pöed display #
# These shows consist of small b/w image animations derived  #
# from gifs.                                                 #
#                                                            #
# by c.guenther[at]mac.com                                   #
#                                                            #
# Date: 01.11.2022                                           #
# Version: X.Y                                               #
#                                                            #
##############################################################
#                                                            #
#    SETUP                                                   #
# ---------------------------------------------------------- #
# every configuration parameter                              #
#                                                            #
# ---------------------------------------------------------- #
# this is ongoing work                                       #
##############################################################

#############################################################################
#                                                                           #
#                                                                           #
#                                            I2C0                           #
#                                                                           #
#     V  V        3  V                       C  C     X     D  P            #
#     B  S  G  3  O  R     G        R     G  S  S     X  G  O  I            #
#     U  Y  N  V  U  E     N        U     N  C  D     X  N  O  R            #
#     S  S  D  N  T  F     D        N     D  L  A     X  D  R  I            #
#  +- -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -+        #
#  |                    28    27 26    22    21 20 19 18    17 16  |  GPIO  #
#  |  40 39 38 37 36 35 34 33 32 31 30 29 28 27 26 25 24 23 22 21  |  PIN   #
#  U                                                               |        #
#  S                                                               |        #
#  B                                                               |        #
#  |                                                               |        #
#  |  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20  |  PIN   #
#  |  0  1     2  3  4  5     6  7  8  9     10 11 12 13    14 15  |  GPIO  #
#  +- -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -+        #
#     F  G  G  T           G              G  T  T  A  A  G  A  A            #
#     I  R  N  R           N              N  S  S  D  D  N  D  D            #
#     R  L  D  E           D              D  D  C  V  V  D  V  V            #
#     E  A     E                             A  L  1  2     3  4            #
#                                                                           #
#                                            I2C1                           #
#                                                                           #
#     ADVx = Adventskranz LED 1-4 (Timed)      F 1-4    --> 12/13/14/15     #
#     FIRE = Fire LED (Evening)                F 5      --> 0               #
#     GRLA = Girlande (from 1st Dec. onward)   F 6      --> 1               #
#     TREE = Christmas Tree (at night)         F 7      --> 2               #
#                                                                           #
#     CEIL = Ceiling LED (ALways on)           A 1                          #
#     DOOL = Door LED    (ALways on)           A 2                          #
#     FIGU = Figure LED  (Always on)           A 3                          #
#                                                                           #
#     CSCL = Clock SCL yellow                           --> 21              #
#     CSDA = Clock SDA green                            --> 20              #
#     DOOR = Door Servo                                 --> 17              #
#     PIRI = PIR Input Pin                              --> 16              #
#     TSCL = Television SCL                             --> 11              #
#     TSDA = Television SDA                             --> 10              #
#     XXXX = not yet used motor or 3 pin input pin      --> 18              #
#                                                                           #
#############################################################################

from logging import getLogger
logger = getLogger(__name__)
logger.setLevel('DEBUG')

class setup:
    parameters = {
        #  DEFINES WHICH HARDWARE FEATURES TO USE
          'use_clock': True         # shall we make use of the real time clock
        , 'use_display': True       # shall we display animations an text on screem
        , 'use_motion_detector': False # shall we check for motion
        , 'use_door': False          # shall we use the door part
        , 'use_door_motor': False   # shall we really drive the door motor
        , 'use_doorbell': False     # shall we use the push button to open the door
        , 'use_sdcard': False       # shall we use an sdcard for the animations
        
        # which leds to use is defined for each led below
        # if it has a valid PIN defined, the led is used
        
        # show the current date and time when no show is shown 
        , 'show_date_and_time_show': True
        #  sleep times after showing the date and time and wait time for the text lines
        , 'sleep_after_date_time_line': 750
        , 'sleep_after_date_time_show': 1500
        # if True, then the number of days until the event are displayed occsionally
        , 'use_countdown': True
        #                 YYYY  MM  DD  HH  mm  ss  tzinfo
        , 'target_date': (2023, 12, 24, 06, 00, 00, 00)
        , 'target_event': 'Weihnachten'
        , 'countdown_last_check_diff': 60000
        
        #
        # ACTIVITY AND DATE AND TIME DEFINTIONS
        #
        # whether or not the show must go on is determined by below lists
        , 'active_at': {'Montag':       [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
                        , 'Dienstag':   [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
                        , 'Mittwoch':   [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
                        , 'Donnerstag': [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
                        , 'Freitag':    [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
                        , 'Samstag':    [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
                        , 'Sonntag':    [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
                        }
        #
        #  PIN DEFINITIONS
        #
        #  OLED - Display
        # is the OLED connected to I2C 0 or 1
        , 'oled_i2c': 0
        , 'oled_sda_pin': 12
        , 'oled_scl_pin': 13
        #
        #  OLED DIMENSIONS
        # dimensions of the oled display
        , 'oled_width': 128
        , 'oled_height': 64
        # pixels for the horizontal and vertical text line positioning
        , 'max_text_height': 60
        , 'line_height': 12
        , 'character_width': 8
        
        #
        #  RTC - Real Tie Clock
        # is the RTC connected to I2C 0 or 1
        , 'rtc_i2c': 0
        , 'rtc_sda_pin': 20
        , 'rtc_scl_pin': 21

        #
        #  PIR - Infrared Receiver
        , 'pir_pin': 21

        #
        #  SERVO - Motor to drive the door
        , 'servo_pin': 17
        , 'motor_drive_freq': 50
        , 'door_closed_position': 4500
        , 'door_opened_position': 7500
        , 'keep_door_closed_for': 120000 #5400000 # 1,5 h *60 min * 60 sec * 1000
        , 'keep_door_opened_for': 20000 #300000   # 5 min * 60 sec * 1000
        , 'door_last_check_diff': 60000
        #
        #  BUTTON - to open the door
        , 'doorbell_pin': 22
        
        #
        #  SDCARD 
        , 'sdcard_sck': 10
        , 'sdcard_mosi': 11
        , 'sdcard_miso': 12
        , 'sdcard_cs': 13
        
        #
        #  CONFIGURATION OF THE STANDARD LEDS
        , 'standard_led_1': {
            'PIN': 25
            , 'NAME': 'OPS LED'
            , 'led_min_on_timer': -1
            , 'led_max_on_timer': -1
            , 'led_min_off_timer': -1
            , 'led_max_off_timer': -1
            , 'led_check_timer': 1
            , 'always_on': False
            , 'is_of_type': 'standard'
            }
        , 'standard_led_2': {
            'PIN': -1
            , 'NAME': 'Table Lantern'
            , 'led_min_on_timer': -1
            , 'led_max_on_timer': -1
            , 'led_min_off_timer': -1
            , 'led_max_off_timer': -1
            , 'led_check_timer': 1
            , 'always_on': True
            , 'is_of_type': 'standard'
            }
        , 'standard_led_3': {
            'PIN': -1
            , 'NAME': 'Christmas Tree'
            , 'led_min_on_timer': 287654
            , 'led_max_on_timer': 734686
            , 'led_min_off_timer': 2265
            , 'led_max_off_timer': 10293
            , 'led_check_timer': 2000
            , 'always_on': False
            , 'is_of_type': 'standard'
            }
        , 'standard_led_4': {
            'PIN': -1
            , 'NAME': 'Front Door Light'
            , 'led_min_on_timer': 62781
            , 'led_max_on_timer': 129876
            , 'led_min_off_timer': 68627
            , 'led_max_off_timer': 129542
            , 'led_check_timer': 5000
            , 'always_on': False
            , 'is_of_type': 'standard'
            }
        , 'standard_led_5': {
            'PIN': -1
            , 'NAME': 'Back Door Light'
            , 'led_min_on_timer': 75765
            , 'led_max_on_timer': 188976
            , 'led_min_off_timer': 81397
            , 'led_max_off_timer': 158736
            , 'led_check_timer': 5000
            , 'always_on': False
            , 'is_of_type': 'standard'
            }
        #
        #  CONFIGURATION OF THE TIMED LEDS
        , 'timed_led_1': {
            'PIN': -1
            , 'NAME': '1. Advent'
            # year month day weekday hour minute second when to turn on
            , 'led_min_on_timer': (2023, 11, 27, 0, 5, 0)
            , 'led_max_on_timer': -1
            , 'led_min_off_timer': -1
            , 'led_max_off_timer': -1
            , 'led_check_timer': 3600000
            , 'always_on': True
            , 'is_of_type': 'timed'
            }
        , 'timed_led_2': {
            'PIN': -1
            , 'NAME': '2. Advent'
            , 'led_min_on_timer': (2023, 12, 4, 0, 5, 0)
            , 'led_max_on_timer': -1
            , 'led_min_off_timer': -1
            , 'led_max_off_timer': -1
            , 'led_check_timer': 3600000
            , 'always_on': True
            , 'is_of_type': 'timed'
            }
        , 'timed_led_3': {
            'PIN': -1
            , 'NAME': '3. Advent'
            , 'led_min_on_timer': (2023, 12, 11, 0, 5, 0)
            , 'led_max_on_timer': -1
            , 'led_min_off_timer': -1
            , 'led_max_off_timer': -1
            , 'led_check_timer': 3600000
            , 'always_on': True
            , 'is_of_type': 'timed'
            }
        , 'timed_led_4': {
            'PIN': -1
            , 'NAME': '4. Advent'
            , 'led_min_on_timer': (2023, 12, 18, 0, 5, 0)
            , 'led_max_on_timer': -1
            , 'led_min_off_timer': -1
            , 'led_max_off_timer': -1
            , 'led_check_timer': 3600000
            , 'always_on': True
            , 'is_of_type': 'timed'
            }
        #
        #  CONFIGURATION OF THE FLICKER LEDS
        , 'flicker_led_1': {
            'PIN': -1
            , 'NAME': 'Flicker 1'
            , 'led_min_on_timer': 5000
            , 'led_max_on_timer': 15000
            , 'led_min_off_timer': 3000
            , 'led_max_off_timer': 9000
            , 'led_check_timer': 2500
            , 'always_on': True
            , 'is_of_type': 'flicker'
            }
        , 'flicker_led_2': {
            'PIN': -1
            , 'NAME': 'Flicker 2'
            , 'led_min_on_timer': 300
            , 'led_max_on_timer': 3000
            , 'led_min_off_timer': 500
            , 'led_max_off_timer': 1000
            , 'led_check_timer': 250
            , 'always_on': True
            , 'is_of_type': 'flicker'
            }
        , 'flicker_led_3': {
            'PIN': -1
            , 'NAME': 'Flicker 3'
            , 'led_min_on_timer': 150
            , 'led_max_on_timer': 1500
            , 'led_min_off_timer': 300
            , 'led_max_off_timer': 700
            , 'led_check_timer': 100
            , 'always_on': True
            , 'is_of_type': 'flicker'
            }
        , 'flicker_led_4': {
            'PIN': -1
            , 'NAME': 'Flicker 4'
            , 'led_min_on_timer': 300
            , 'led_max_on_timer': 3000
            , 'led_min_off_timer': 500
            , 'led_max_off_timer': 1000
            , 'led_check_timer': 250
            , 'always_on': True
            , 'is_of_type': 'flicker'
            }
        , 'flicker_led_5': {
            'PIN': -1
            , 'NAME': 'Flicker 5'
            , 'led_min_on_timer': 5000
            , 'led_max_on_timer': 15000
            , 'led_min_off_timer': 3000
            , 'led_max_off_timer': 9000
            , 'led_check_timer': 2500
            , 'always_on': True
            , 'is_of_type': 'flicker'
            }
        #
        #  CONFIGURATION OF THE FADER LEDS
        , 'fader_led_1': {
            'PIN': -1
            , 'NAME': 'Fader 1'
            , 'led_min_on_timer': 0      # cycle up from
            , 'led_max_on_timer': 65025  # cycle up to
            , 'led_min_off_timer': 0     # cycle down to
            , 'led_max_off_timer': 65025 # cycle down from 
            , 'led_check_timer': 100     # cycle steps
            , 'always_on': True
            , 'is_of_type': 'fader'
            }
        , 'fader_led_2': {
            'PIN': -1
            , 'NAME': 'Fader 2'
            , 'led_min_on_timer': 0
            , 'led_max_on_timer': 65025
            , 'led_min_off_timer': 0
            , 'led_max_off_timer': 65025
            , 'led_check_timer': 10
            , 'always_on': True
            , 'is_of_type': 'fader'
            }
        , 'fader_led_3': {
            'PIN': -1
            , 'NAME': 'Fader 3'
            , 'led_min_on_timer': 0
            , 'led_max_on_timer': 65025
            , 'led_min_off_timer': 0
            , 'led_max_off_timer': 65025
            , 'led_check_timer': 100
            , 'always_on': True
            , 'is_of_type': 'fader'
            }
        , 'fader_led_4': {
            'PIN': -1
            , 'NAME': 'Fader 4'
            , 'led_min_on_timer': 0
            , 'led_max_on_timer': 65025
            , 'led_min_off_timer': 0
            , 'led_max_off_timer': 65025
            , 'led_check_timer': 1000
            , 'always_on': True
            , 'is_of_type': 'fader'
            }
        , 'fader_led_5': {
            'PIN': -1
            , 'NAME': 'Fader 5'
            , 'led_min_on_timer': 0
            , 'led_max_on_timer': 65025
            , 'led_min_off_timer': 0
            , 'led_max_off_timer': 65025
            , 'led_check_timer': 2000
            , 'always_on': True
            , 'is_of_type': 'fader'
            }
        
        #
        # COUNTERs AND TIMERs
        #
        # defines after how many 5 second sleeps, a whole 5 minute sleep should be started
        # in the main loop when NOT in active hours
        , 'max_counter_for_short_sleep': 12
        # while not in the activity hours there are two sleep cycles,
        # a 5 second sleep and after 12 times 5 seconds 
        , 'no_active_hours_short_sleep_between_checks_in_ms': 5000
        # a whole 5 minutes sleep
        , 'no_active_hours_long_sleep_between_checks_in_ms': 300000
        
        
        # waittime in ms after a show sequence is run before a new chech on movement is done
          # and consequently (in case there is movement) until a new show sequence is started
        , 'sleep_after_show_in_ms': 1750
        
        
        # how long in ms between checks for movememnt
        , 'sleep_between_checks_in_ms': 1757
        # regardless of detected movement, the show shall start every 120.000 ms (every 2 minutes)
        , 'show_something_every_x_ms': 120000
        
        #
        # GENERIC STUFF
        # generic On or Off
        , 'OFF': 0
        , 'ON': 1
        
        # used for displaying the weekday during pause shows
        , 'weekdays': {1: 'Montag'
                        , 2: 'Dienstag'
                        , 3: 'Mittwoch'
                        , 4: 'Donnerstag'
                        , 5: 'Freitag'
                        , 6: 'Samstag'
                        , 0: 'Sonntag'
                        }
        # To store number of days in all months from January to December
        # used to calculate the number of days between two given dates (actually currently not used)
        , 'monthDays': [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        #
        #  BELOW ARE THE CONFIG PARAMTER FOR THE SHOWS
        #
        # Directories
        , 'anim_dir': 'anim'
        , 'intro_dir': 'intro'
        , 'show_dir': 'show'
        , 'pause_dir': 'pause'
        , 'after_dir': 'after'
        
        #
        # Probability that an intro or after show is shown
        # is determined by a random selection of 0 - x
        , 'probability_for_the_intro_show': 3
        , 'probability_for_the_after_show': 3
        
        #
        #  BEFORE THE SHOW TEXT
        #  
        #  if show_before_the_show_text is set to True on a show, this is shown
        #
        # must always be 1
        , 'min_before_the_show_text_number': 1
        # max number of the text elements
        # is dynamically determined on initialization
        , 'max_before_the_show_text_number': 3
        # how many text elements shall be shown
        , 'before_the_show_text_number_to_show': 6
        , 'sleep_after_before_the_show_text_line': 750
        , 'sleep_after_before_the_show_text_text': 2000
        , 'before_the_show_text_greeting_text': {1: ['Lieber'
                                            , 'Weihnachtsmann'
                                            , 'ich moechte'
                                            ]
                                        , 2: ['Ich wuensche'
                                            , 'mir zu'
                                            , 'Weihnachten'
                                            ]
                                        , 3: ['Mein'
                                            , 'Wunschzettel'
                                            , ''
                                            ]
                                        }
        , 'before_the_show_text_text': ['ein Auto'
                            , 'Lego Friends'
                            , 'Playmobil'
                            , 'eine Rakete'
                            , 'ganz viel Geld'
                            , 'Gesundheit'
                            , 'Freunde'
                            , 'eine Uhr'
                            , 'ein Schlagzeug'
                            , 'eine Gitarre'
                            , 'Bonbons'
                            , 'eine Puppe'
                            , 'ein Auto'
                            , 'ne Playstation'
                            , 'Nintendo Switch'
                            , 'Weltfrieden'
                            , 'eine Barbiepuppe'
                            , 'Lego Friends'
                            , 'einen Fussball'
                            , 'tolle Noten'
                            , 'Schnickschnack'
                            , 'Schokolade'
                            , 'Schlickersachen'
                            , 'Socken'
                            , 'Kombutah'
                            , 'ein Smartphone'
                            , 'ein Spiel'
                            , 'Taucherbrille'
                            , 'ein Brettspiel'
                            , 'Blumentopf'
                            ]

        #
        #  AFTER THE SHOW TEXT
        #  
        #  if show_after_the_show_text is set to True on a show, this is shown after the show
        #
        # must always be 1
        , 'min_after_the_show_text_number': 1
        # max number of the text elements
        # is dynamically determined on initialization
        , 'max_after_the_show_text_number': 3
        # how many text elements shall be shown
        , 'after_the_show_text_to_show': 6
        , 'sleep_after_after_the_show_text_line': 750
        , 'sleep_after_after_the_show_text_text': 2000
        , 'after_the_show_text_greeting_text': {1: []
                                    , 2: []
                                    , 3: []
                                    }
        , 'after_the_show_text_text': []


        #
        #  ANIMATIONS FOR THE SHOW
        #
        # generic settings for shows without own settings
        , 'generic': {'title': 'New'
                      , 'repetitions': 1
                      , 'invert_color': 1
                      , 'invert_prior_show': True
                      , 'image_pause': 100
                      , 'sleep_after_animation': 1
                      , 'sleep_after_text_line': 200
                      , 'sleep_after_greeting': 1500
                      , 'sleep_after_end': 1
                      , 'intro_text': []
                      , 'end_text': []
                      , 'show_before_the_show_text': False
                      , 'show_after_the_show_text': False
                      , 'show_date_time_text': False
                      , 'show_countdown_text': False
                      }
        #
        #  THE INTRO SHOWS
        #
        # Testbild
        , 'tbild': {'title': 'Testbild'
                    , 'repetitions': 1
                    , 'invert_color': 1
                    , 'invert_prior_show': True
                    , 'image_pause': 750
                    , 'sleep_after_animation': 1000
                    , 'sleep_after_text_line': 500
                    , 'sleep_after_greeting': 2000
                    , 'sleep_after_end': 250
                    , 'intro_text': ['Elfen-TV'
                                    , ''
                                    , 'Das'
                                    , 'Weihnachts'
                                    , 'fernsehen'
                                    ]
                    , 'end_text': []
                    , 'show_before_the_show_text': False
                    , 'show_after_the_show_text': False
                    , 'show_date_time_text': False
                    , 'show_countdown_text': True
                    }
        # count up 1-4
        , 'intro2': {'title': 'Intro 2'
                    , 'repetitions': 1
                    , 'invert_color': 1
                    , 'invert_prior_show': True
                    , 'image_pause': 500
                    , 'sleep_after_animation': 1000
                    , 'sleep_after_text_line': 0
                    , 'sleep_after_greeting': 1000
                    , 'sleep_after_end': 1000
                    , 'intro_text': ['Weihnachts'
                                     , 'fernsehen'
                                     , 'von'
                                     , 'Elfen-TV'
                                     ]
                    , 'end_text': []
                    , 'show_before_the_show_text': False
                    , 'show_after_the_show_text': False
                    , 'show_date_time_text': False
                    , 'show_countdown_text': True
                    }

        #
        #   THE MAIN SHOW
        #
        # Tom und Jerry Cartoon
        , 'tomje': {'title': 'Tom und Jerry'
                    , 'repetitions': 1
                    , 'invert_color': 1
                    , 'invert_prior_show': True
                    , 'image_pause': 150
                    , 'sleep_after_animation': 750
                    , 'sleep_after_text_line': 250
                    , 'sleep_after_greeting': 2000
                    , 'sleep_after_end': 1
                    , 'intro_text': ['Elfen-TV'
                                    , 'praesentiert'
                                    , ''
                                    , 'Tom und Jerry']
                    , 'end_text': []
                    , 'show_before_the_show_text': False
                    , 'show_after_the_show_text': False
                    , 'show_date_time_text': False
                    , 'show_countdown_text': False
                    }
        # Mickey und Pluto machen Musik
        , 'mplut': {'title': 'Mickey und Pluto'
                   , 'repetitions': 1
                   , 'invert_color': 1
                   , 'invert_prior_show': True
                   , 'image_pause': 150
                   , 'sleep_after_animation': 1000
                   , 'sleep_after_text_line': 1
                   , 'sleep_after_greeting': 1
                   , 'sleep_after_end': 1
                   , 'intro_text': []
                   , 'end_text': []
                   , 'show_before_the_show_text': False
                   , 'show_after_the_show_text': False
                   , 'show_date_time_text': False
                   , 'show_countdown_text': False
                   }
        # Christmas Pictures
        , 'cpict': {'title': 'Christmas Pictures'
                    , 'repetitions': 1
                    , 'invert_color': 1
                    , 'invert_prior_show': True
                    , 'image_pause': 1000
                    , 'sleep_after_animation': 1000
                    , 'sleep_after_text_line': 1
                    , 'sleep_after_greeting': 1
                    , 'sleep_after_end': 1
                    , 'intro_text': []
                    , 'end_text': []
                    , 'show_before_the_show_text': False
                    , 'show_after_the_show_text': False
                    , 'show_date_time_text': False
                    , 'show_countdown_text': False
                    }
        # a rider doing horse jumps
        , 'horse': {'title': 'Der wilde Reiter'
                    , 'repetitions': 5
                    , 'invert_color': 0
                    , 'invert_prior_show': True
                    , 'image_pause': 100
                    , 'sleep_after_animation': 250
                    , 'sleep_after_text_line': 750
                    , 'sleep_after_greeting': 2000
                    , 'sleep_after_end': 2000
                    , 'intro_text': [''
                                   , 'Er reitet'
                                   , 'wie ein'
                                   , 'Teufel'
                                   , ''
                                   , 'Elfen-TV'
                                   , 'praesentiert'
                                   , ''
                                   , 'Der Reiter'
                                   ]
                    , 'end_text': ['Wahnsinn']
                    , 'show_before_the_show_text': False
                    , 'show_after_the_show_text': False
                    , 'show_date_time_text': False
                    , 'show_countdown_text': False
                    }
        # Metropolis
        , 'metro': {'title': 'Metropolis'
                    , 'repetitions': 3
                    , 'invert_color': 1
                    , 'invert_prior_show': True
                    , 'image_pause': 200
                    , 'sleep_after_animation': 1000
                    , 'sleep_after_text_line': 750
                    , 'sleep_after_greeting': 2000
                    , 'sleep_after_end': 2000
                    , 'intro_text': ['Heute im'
                                   , 'Elfen-TV'
                                   , ''
                                   , 'ein Klassiker'
                                   , 'des Films'
                                   , ''
                                   , 'Fritz Langs'
                                   , ''
                                   , 'Metropolis'
                                   , ''
                                   ]
                    , 'end_text': []
                    , 'show_before_the_show_text': False
                    , 'show_after_the_show_text': False
                    , 'show_date_time_text': False
                    , 'show_countdown_text': False
                    }
        # nosferatu dies
        , 'nosfe': {'title': 'Nosferatu'
                    , 'repetitions': 1
                    , 'invert_color': 1
                    , 'invert_prior_show': True
                    , 'image_pause': 200
                    , 'sleep_after_animation': 1000
                    , 'sleep_after_text_line': 750
                    , 'sleep_after_greeting': 2000
                    , 'sleep_after_end': 2000
                    , 'intro_text': [''
                                   , 'Heute im'
                                   ,'Gruselkanal'
                                   , 'des Elfen-TV'
                                   , ''
                                   , ''
                                   , 'Nosferatu'
                                   , '...'
                                   , 'Eine Symphonie'
                                   , 'des Grauens'
                                   ]
                    , 'end_text': ['Keine Uhr?'
                                 , ''
                                 , 'Schade'
                                 , 'Schokolade'
                                 , ''
                                 , ''
                                 , 'Friedrich'
                                 , 'Wilhelm'
                                 , 'Murnau'
                                 , '1922'
                                 ]
                    , 'show_before_the_show_text': False
                    , 'show_after_the_show_text': False
                    , 'show_date_time_text': False
                    , 'show_countdown_text': False
                    }
        # Pluto ruins a kiss
        , 'pluto': {'title': 'Pluto'
                    , 'repetitions': 1
                    , 'invert_color': 1
                    , 'invert_prior_show': True
                    , 'image_pause': 100
                    , 'sleep_after_animation': 1
                    , 'sleep_after_text_line': 200
                    , 'sleep_after_greeting': 1500
                    , 'sleep_after_end': 1
                    , 'intro_text': ['Wenn ein'
                                   , 'Hund zur'
                                   , 'falschen Zeit'
                                   , 'auftaucht'
                                   ]
                    , 'end_text': []
                    , 'show_before_the_show_text': False
                    , 'show_after_the_show_text': False
                    , 'show_date_time_text': False
                    , 'show_countdown_text': False
                    }
        # Mickey Mouse steamboat willie
        , 'sboat': {'title': 'Steamboat Willie'
                    , 'repetitions': 2
                    , 'invert_color': 1
                    , 'invert_prior_show': True
                    , 'image_pause': 200
                    , 'sleep_after_animation': 1000
                    , 'sleep_after_text_line': 500
                    , 'sleep_after_greeting': 3000
                    , 'sleep_after_end': 2000
                    , 'intro_text': [''
                                   , 'Heute'
                                   , 'exklusiv und'
                                   , 'erstmalg im'
                                   , 'Elfen-TV'
                                   , ''
                                   , ''
                                   , 'Steamboat'
                                   , 'Willie'
                                   ]
                    , 'end_text': ['Was fuer ein'
                                  , 'Mordskerl'
                                  , 'dieser'
                                  , 'Mickey Mouse'
                                  ]
                    , 'show_before_the_show_text': False
                    , 'show_after_the_show_text': False
                    , 'show_date_time_text': False
                    , 'show_countdown_text': False
                    }

        #
        #  Pause Animations 
        #
        , 'paus2': {'title': 'Kurze pause'
                    , 'repetitions': 1
                    , 'invert_color': 0
                    , 'invert_prior_show': True
                    , 'image_pause': 200
                    , 'sleep_after_animation': 3000
                    , 'sleep_after_text_line': 200
                    , 'sleep_after_greeting': 1500
                    , 'sleep_after_end': 250
                    , 'intro_text': ['Kurze Pause']
                    , 'end_text': []
                    , 'show_before_the_show_text': False
                    , 'show_after_the_show_text': False
                    , 'show_date_time_text': True
                    , 'show_countdown_text': False
                    }
        , 'paus3': {'title': 'Sendepause'
                    , 'repetitions': 1
                    , 'invert_color': 1
                    , 'invert_prior_show': True
                    , 'image_pause': 200
                    , 'sleep_after_animation': 3000
                    , 'sleep_after_text_line': 200
                    , 'sleep_after_greeting': 1500
                    , 'sleep_after_end': 250
                    , 'intro_text': ['Sendepause']
                    , 'end_text': []
                    , 'show_before_the_show_text': False
                    , 'show_after_the_show_text': False
                    , 'show_date_time_text': True
                    , 'show_countdown_text': False
                    }

        #
        # SANTA CLAUSE and the CHRISTMAS ELVES
        #
        # Santa clause brings a present
        , 'santa': {'title': 'Santa Clause'
                    , 'repetitions': 1
                    , 'invert_color': 1
                    , 'invert_prior_show': True
                    , 'image_pause': 200
                    , 'sleep_after_animation': 1
                    , 'sleep_after_text_line': 750
                    , 'sleep_after_greeting': 1500
                    , 'sleep_after_end': 1
                    , 'intro_text': []
                    , 'end_text': ['Ho Ho Ho'
                                   , ''
                                   , 'Hier kommt'
                                   , 'Santa']
                    , 'show_before_the_show_text': True
                    , 'show_after_the_show_text': False
                    , 'show_date_time_text': False
                    , 'show_countdown_text': False
                    }
        # Santa flies over a house
        , 'sant2': {'title': 'Santa Flying'
                    , 'repetitions': 1
                    , 'invert_color': 1
                    , 'invert_prior_show': True
                    , 'image_pause': 200
                    , 'sleep_after_animation': 1
                    , 'sleep_after_text_line': 750
                    , 'sleep_after_greeting': 1500
                    , 'sleep_after_end': 1
                    , 'intro_text': ['Der'
                                   , 'Weihnachtsmann'
                                   , 'fliegt zu'
                                   , 'Dir']
                    , 'end_text': []
                    , 'show_before_the_show_text': True
                    , 'show_after_the_show_text': False
                    , 'show_date_time_text': False
                    , 'show_countdown_text': False
                    }
        # Santa sneaks silently
        , 'sant3': {'title': 'Sneaky Santa'
                    , 'repetitions': 5
                    , 'invert_color': 1
                    , 'invert_prior_show': True
                    , 'image_pause': 0
                    , 'sleep_after_animation': 1
                    , 'sleep_after_text_line': 750
                    , 'sleep_after_greeting': 1500
                    , 'sleep_after_end': 1
                    , 'intro_text': ['Wer schleicht'
                                     , 'sich denn'
                                     , 'da in dein'
                                     , 'Haus?'
                                     ]
                    , 'end_text': [''
                                   , 'Es ist'
                                   , 'Santa Klaus']
                    , 'show_before_the_show_text': True
                    , 'show_after_the_show_text': False
                    , 'show_date_time_text': False
                    , 'show_countdown_text': False
                    }
        }
    
    def __init__(self):
        logger.info('init setup class')
    def getConfigParameter(self, parameter):
        return(self.parameters.get(parameter))
    def getConfigElementFromList(self, parameter, element):
        listobject = self.parameters.get(parameter)
        return(listobject.get(element))
    def getElementFromArray(self, array, element):
        listobject = self.parameters.get(array)
        return(listobject[element])
    