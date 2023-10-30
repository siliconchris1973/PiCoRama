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
# Version: 1.0                                               #
#                                                            #
# ---------------------------------------------------------- #
# Display part partly based on work from peppe8o             #
#                                                            #
##############################################################
#                                                            #
#   DISPLAY                                                  #
# ---------------------------------------------------------- #
#                                                            #
# Display image sequences or text on the oled display        #
# The displayed images are jpegs extracted from a gif        #
# sequence                                                   #
#                                                            #
#  to extract the jpgs from a gif:                           #
#       convert <name>.gif JPG/%02d.jpg                      #
#  to scale the files so they fit the oled:                  #
#  for i in *.jpg ; do convert -extract 85x64 $i $i ; done   #
#                                                            #
# ---------------------------------------------------------- #
# V1.0 ß1.11.2022 initial release                            #
##############################################################
from machine import Pin, I2C
import framebuf, ssd1306
import time
import os, json
import random
import uasyncio as asyncio
from logging import getLogger
logger = getLogger(__name__)
logger.setLevel('INFO')

class display:
    ON = 1
    OFF = 0
    
    increment = 12
    character_width = 8
    max_text_height = 60
    oled_height = 64
    oled_width = 128
    
    anim_dir = ''
    intro_dir = ''
    pause_dir = ''
    after_dir = ''
    show_dir = ''
    
    the_shows = {
        # we need an array of shows for numbering the show and
        # a dictionary associating show names with directories
        'the_intros': []
        , 'the_shows': []
        , 'the_pauses': []
        , 'the_afters': []
        , 'the_intros_dict': []
        , 'the_shows_dict': []
        , 'the_pauses_dict': []
        , 'the_afters_dict': []
        }
    
    def __init__(self, setup, clock):
        self.setup = setup
        self.clock = clock
        
        self.use_display = self.setup.getConfigParameter('use_display')
        
        self.ON = self.setup.getConfigParameter('ON')
        self.OFF = self.setup.getConfigParameter('OFF')
        
        self.display_status = self.OFF
        
        # the show numbers below are all used to make sure we do not show the same show all the time
        self.increment = self.setup.getConfigParameter('line_height') #12
        self.character_width = self.setup.getConfigParameter('character_width') #8
        self.max_text_height = self.setup.getConfigParameter('max_text_height')
        self.oled_height = self.setup.getConfigParameter('oled_height')
        self.oled_width = self.setup.getConfigParameter('oled_width')
        
        self.the_intro_show_number = 0
        self.last_intro_show_number = 0
        self.max_intro_show_number = 0
        self.probability_for_the_intro_show = self.setup.getConfigParameter('probability_for_the_intro_show')
        
        self.the_show_number = 0
        self.last_show_number = 0
        self.max_show_number = 0
        
        self.the_pause_show_number = 0
        self.last_pause_show_number = 0
        self.max_pause_show_number = 0
        
        self.the_after_show_number = 0
        self.last_after_show_number = 0
        self.max_after_show_number = 0
        self.probability_for_the_after_show = self.setup.getConfigParameter('probability_for_the_after_show')
        
        self.sleep_after_date_time_line = self.setup.getConfigParameter('sleep_after_date_time_line')
        self.sleep_after_date_time_show = setup.getConfigParameter('sleep_after_date_time_show')
        
        self.sleep_after_before_the_show_text_line = self.setup.getConfigParameter('sleep_after_before_the_show_text_line')
        self.sleep_after_before_the_show_text_text = self.setup.getConfigParameter('sleep_after_before_the_show_text_text')
        
        self.sleep_after_after_the_show_text_text = self.setup.getConfigParameter('sleep_after_after_the_show_text_text')
        self.sleep_after_after_the_show_text_line = self.setup.getConfigParameter('sleep_after_after_the_show_text_line')
        
        self.min_after_the_show_text_number = self.setup.getConfigParameter('min_after_the_show_text_number')
        self.max_after_text_show_number = self.setup.getConfigParameter('max_after_text_show_number')
        self.after_the_show_text_greeting_text = self.setup.getConfigParameter('after_the_show_text_greeting_text')
        self.after_the_show_text_to_show = self.setup.getConfigParameter('after_the_show_text_to_show')
        self.min_before_the_show_text_number = self.setup.getConfigParameter('min_before_the_show_text_number')
        self.max_before_the_show_text_number= self.setup.getConfigParameter('max_before_the_show_text_number')
        self.before_the_show_text_greeting_text = self.setup.getConfigParameter('before_the_show_text_greeting_text')
        self.before_the_show_text_number_to_show= self.setup.getConfigParameter('before_the_show_text_number_to_show')
        self.after_the_show_text_text = self.setup.getConfigParameter('after_the_show_text_text')
        self.before_the_show_text_text = self.setup.getConfigParameter('before_the_show_text_text')
            
        self.target_event = self.setup.getConfigParameter('target_event')
        
        # setup the I2C communication
        if self.use_display == True:
            self.i2c = I2C(self.setup.getConfigParameter('oled_i2c'), sda=Pin(self.setup.getConfigParameter('oled_sda_pin')), scl=Pin(self.setup.getConfigParameter('oled_scl_pin')))
            self.oled = ssd1306.SSD1306_I2C(self.oled_width, self.oled_height, self.i2c)
            try:
                self.oled = ssd1306.SSD1306_I2C(self.oled_width, self.oled_height, self.i2c)
            except Exception as e:
                logger.error('could not initialize the display: ') + str(e)
        
        logger.info('init display class')
        logger.debug(' i2c ' + str(self.setup.getConfigParameter('oled_i2c'))
                     + ' sda pin ' + str(self.setup.getConfigParameter('oled_sda_pin'))
                     + ' scl pin ' + str(self.setup.getConfigParameter('oled_scl_pin'))
                  )
        self.poweroff()
        
        logger.info('init the shows')
        self.anim_dir = self.setup.getConfigParameter('anim_dir')
        self.intro_dir = self.setup.getConfigParameter('intro_dir')
        self.pause_dir = self.setup.getConfigParameter('pause_dir')
        self.show_dir = self.setup.getConfigParameter('show_dir')
        self.after_dir = self.setup.getConfigParameter('after_dir')
        self.initTheShows()
        
    def getStatus(self):
        return(self.display_status)
    def poweron(self):
        self.display_status = self.ON
        logger.debug('Display on')
        
        if self.use_display == True:
            self.oled.poweron()
        return(self.display_status)
    def poweroff(self):
        self.display_status = self.OFF
        logger.debug('Display off')
        
        if self.use_display == True:
            self.oled.poweroff()
        return(self.display_status)
    
    def createTheShow(self):
        # create a list of shows Consisting of a pause or intro show, the main and the after show
        the_show = []
        
        #
        # START WITH AN INTRO SHOW
        #
        if (random.randint(0,self.probability_for_the_intro_show) == 0):
            while self.the_intro_show_number == self.last_intro_show_number:
                self.the_intro_show_number = random.randint(0, self.max_intro_show_number)
            self.last_intro_show_number = self.the_intro_show_number
            
            logger.debug('appending the intro show ' + str(self.the_intro_show_number))
            the_show.append(self.getTheShowDict(self.the_intro_show_number, 'i'))
        
        #
        # THEN SHOW THE MAIN SHOW
        #
        while self.the_show_number == self.last_show_number:
            self.the_show_number = random.randint(0, self.max_show_number)
        self.last_show_number = self.the_show_number
        
        logger.debug('appending the main show ' + str(self.the_show_number))
        the_show.append(self.getTheShowDict(self.the_show_number, 's'))
        
        #
        # THEN A PAUSE SHOW
        #
        while self.the_pause_show_number == self.last_pause_show_number:
            self.the_pause_show_number = random.randint(0, self.max_pause_show_number)
        self.last_pause_show_number = self.the_pause_show_number
        
        logger.debug('appending the pause show ' + str(self.the_pause_show_number))
        the_show.append(self.getTheShowDict(self.the_pause_show_number, 'p'))
        
        #
        # THEN THE AFTER SHOW
        #
        if (random.randint(0,self.probability_for_the_after_show) == 0):
            while self.the_after_show_number == self.last_after_show_number:
                self.the_after_show_number = random.randint(0, self.max_after_show_number)
            self.last_after_show_number = self.the_after_show_number
            
            logger.debug('appending the after show ' + str(self.the_after_show_number))
            the_show.append(self.getTheShowDict(self.the_after_show_number, 'a'))
        
        return(the_show)
    
       
    #
    #   DISPLAY THE SHOW SEQUENCE 
    #
    def displayTheShow(self, animation):
        # first get all the animation data from the setup file
        title, directory, invert_color, invert_prior_show, image_pause, sleep_after_animation, repetitions, sleep_after_text_line, sleep_after_greeting, sleep_after_end, greeting_text, end_text, show_before_the_show_text, show_after_the_show_text, show_date_time_text, show_countdown_text = self.getShowParameter(animation)
        
        # this should not happen anymore
        if directory == -1:
            logger.error('BIG ERROR IN SETTING UP THE SHOW - ABORTING')
            return(-1)
        
        logger.info('Displaying '+str(title)+' animation from dir ' + str(directory))
        
        if self.use_display == True:
            #
            #  SHOW DAYS UNTIL THE COUNTDOWN DATE
            #  before showing the before show text, we may show the days until countdown
            #
            if show_countdown_text == True:
                logger.debug('show '+str(title)+' countdown text')
                
                #asyncio.run(self.showDateTimeOrCountDown('c'))
                #self.showDateTimeOrCountDown('c')
                
            #
            #  SHOW BEFORE THE SHOW TEXT
            #
            if show_before_the_show_text == True:
                logger.debug('show '+str(title)+' before-the-show text')
                
                before_the_show_text_text = self.getBeforeOrAftershowText(False)
                asyncio.run(self.showText(before_the_show_text_text, False, False, self.sleep_after_before_the_show_text_line, self.sleep_after_before_the_show_text_text))
                self.fillScreen(0) # clear the screen
                
            #  INVERT COLOR
            if invert_prior_show == True:
                self.invertScreen(0) # war beides 0 / invert_color
                self.fillScreen(0) # clear the screen
            
            #
            #  SHOW GREETINGS TEXT
            #
            if len(greeting_text) > 0:
                logger.debug('show '+str(title)+' greeting text')
                
                self.invertScreen(0)
                asyncio.run(self.showText(greeting_text, True, True, sleep_after_text_line, sleep_after_greeting))
                self.fillScreen(0)
            
            #
            #  SHOW DATE AND TIME
            #  after the intro of a pause show, we may show the time and date
            #
            if show_date_time_text == True:
                logger.debug('show '+str(title)+' date time text')
                
                #asyncio.run(self.showDateTimeOrCountDown('d'))
                #self.showDateTimeOrCountDown('d')
            self.invertScreen(invert_color)
            self.fillScreen(invert_color)
            
            #
            #  SHOW THE IMAGE SEQUENCE OF THE SHOW
            #
            logger.debug('show '+str(title)+' image sequence then sleep for ' +str(sleep_after_animation)+ ' ms')
            
            asyncio.run(self.showImageSequence(directory, invert_color, image_pause, repetitions, sleep_after_animation))
            
            #  INVERT COLOR
            if invert_prior_show == True:
                self.invertScreen(0) # war beides 0 / invert_color
                self.fillScreen(0) # clear the screen
            
            #
            #  SHOW END TEXT
            #
            if len(end_text) > 0:
                logger.debug('show '+str(title)+' end text')
                
                asyncio.run(self.showText(end_text, True, True, sleep_after_text_line, sleep_after_end))
                self.fillScreen(0) # clear the screen
                
            #
            #  SHOW AFTER SHOW TEXT
            #
            if show_after_the_show_text == True:
                logger.debug('show '+str(title)+' after_the_show_text text')
                
                after_the_show_text_text = self.getBeforeOrAftershowText(True)
                asnycio.run(self.showText(after_the_show_text_text, False, False, self.sleep_after_after_the_show_text_line, self.sleep_after_after_the_show_text_text))
                self.showText(after_the_show_text_text, False, False, self.sleep_after_after_the_show_text_line, self.sleep_after_after_the_show_text_text)
                self.fillScreen(0) # clear the screen
            logger.debug('Its the end of the show as we know it')
        else:
            logger.debug('   Sleeping for 5 seconds to make up for omitted animation')
            time.sleep_ms(5000)
        
        self.fillScreen(0)
    
    #
    #   RETRIEVE THE SHOW PARAMTERS FROM THE SD CARD
    #
    def getConfigFile(self, file):
        the_show = json.load( open( directory+'/settings.json' ) )
        print(the_show)
    
    # returns which show to show                        i=intro, s=show, p=pause, a=after
    def getTheShowDict(self, the_show_number, show_type='s'):
        logger.debug('getting the show dict for show number ' + str(the_show_number) + ' of type ' + str(show_type))
        return_the_show=[]
        if show_type == 'i':
            the_shows = self.the_shows.get('the_intros')
            the_shows_dict = self.the_shows.get('the_intros_dict')
        elif show_type == 'p':
            the_shows = self.the_shows.get('the_pauses')
            the_shows_dict = self.the_shows.get('the_pauses_dict')
        elif show_type == 's':
            the_shows = self.the_shows.get('the_shows')
            the_shows_dict = self.the_shows.get('the_shows_dict')
        else:
            the_shows = self.the_shows.get('the_afters')
            the_shows_dict = self.the_shows.get('the_afters_dict')
        logger.trace('returning ' + str(the_shows) + ' -> ' + str(the_shows_dict))
        the_show = the_shows[the_show_number-1]
        return_the_show.append(the_show)
        return_the_show.append(the_shows_dict[the_show])
        
        return(return_the_show)
    
    # returns all parameters for a show
    def getShowParameter(self, animation):
        show=animation[0]
        directory=animation[1]
        logger.trace('retrieving everything for show ' + str(show) + ' from dir ' + str(directory))
        
        title = self.setup.getConfigElementFromList('generic', 'title')
        invert_color = self.setup.getConfigElementFromList('generic', 'invert_color')
        invert_prior_show = self.setup.getConfigElementFromList('generic', 'invert_prior_show')
        image_pause = self.setup.getConfigElementFromList('generic', 'image_pause')
        sleep_after_animation = self.setup.getConfigElementFromList('generic', 'sleep_after_animation')
        repetitions = self.setup.getConfigElementFromList('generic', 'repetitions')
        sleep_after_text_line = self.setup.getConfigElementFromList('generic', 'sleep_after_text_line')
        sleep_after_greeting = self.setup.getConfigElementFromList('generic', 'sleep_after_greeting')
        sleep_after_end = self.setup.getConfigElementFromList('generic', 'sleep_after_end')
        intro_text = self.setup.getConfigElementFromList('generic', 'intro_text')
        end_text = self.setup.getConfigElementFromList('generic', 'end_text')
        show_before_the_show_text = self.setup.getConfigElementFromList('generic', 'show_before_the_show_text')
        show_after_the_show_text = self.setup.getConfigElementFromList('generic', 'show_after_the_show_text')
        show_date_time_text = self.setup.getConfigElementFromList('generic', 'show_date_time_text')
        show_countdown_text = self.setup.getConfigElementFromList('generic', 'show_countdown_text')
        
        try:
            the_show = self.setup.getConfigParameter(show)
            title = the_show.get('title')
            invert_color = the_show.get('invert_color')
            invert_prior_show = the_show.get('invert_prior_show')
            image_pause = the_show.get('image_pause')
            sleep_after_animation = the_show.get('sleep_after_animation')
            repetitions = the_show.get('repetitions')
            sleep_after_text_line = the_show.get('sleep_after_text_line')
            sleep_after_greeting = the_show.get('sleep_after_greeting')
            sleep_after_end = the_show.get('sleep_after_end')
            show_before_the_show_text = the_show.get('show_before_the_show_text')
            show_after_the_show_text = the_show.get('show_after_the_show_text')
            show_date_time_text = the_show.get('show_date_time_text')
            show_countdown_text = the_show.get('show_countdown_text')
            intro_text = the_show.get('intro_text')
            end_text = the_show.get('end_text')
        except:
            logger.warning('could not get animation settings for '+str(show)+' - using defaults')
        
        logger.crazy('returning title ' + str(title)
                  +' / directory ' + str(directory)
                  +' / invert_color ' + str(invert_color)
                  +' / invert_prior_show ' + str(invert_prior_show)
                  +' / image_pause ' + str(image_pause)
                  +' / sleep_after_animation ' + str(sleep_after_animation)
                  +' / repetitions ' + str(repetitions)
                  +' / sleep_after_text_line ' + str(sleep_after_text_line)
                  +' / sleep_after_greeting ' + str(sleep_after_greeting)
                  +' / sleep_after_end ' + str(sleep_after_end)
                  +' / intro_text ' + str(intro_text)
                  +' / end_text ' + str(end_text)
                  +' / show_before_the_show_text ' + str(show_before_the_show_text)
                  +' / show_after_the_show_text ' + str(show_after_the_show_text)
                  +' / show_date_time_text ' + str(show_date_time_text)
                  +' / show_countdown_text ' + str(show_countdown_text)
                  )
        return(title, directory, invert_color, invert_prior_show, image_pause, sleep_after_animation, repetitions, sleep_after_text_line, sleep_after_greeting, sleep_after_end, intro_text, end_text, show_before_the_show_text, show_after_the_show_text, show_date_time_text, show_countdown_text)
    
    
    #
    #  INIT THE SHOWS ON STARTUP
    #
    def initTheShows(self):
        logger.debug('setting up the shows')
        #
        # fill the list of intro shows
        #
        counter = 0
        the_shows = []
        the_shows_dict = {}
        logger.debug('init intro shows')
        for element in os.listdir(self.anim_dir+'/'+self.intro_dir+'/'):
            directory = self.anim_dir+'/'+self.intro_dir+'/'+element
            the_shows.append(element)
            the_shows_dict[element] = directory
            counter += 1
            logger.trace('  -> ' + str(counter) + ' ' + str(element) + '=' + str(directory))
        self.the_shows['the_intros'] = the_shows
        self.the_shows['the_intros_dict'] = the_shows_dict
        self.the_shows['max_intro_show_number'] = counter
        self.max_intro_show_number = counter
        #
        # fill the list of main shows
        #
        counter = 0
        the_shows = []
        the_shows_dict = {}
        logger.debug('init main shows')
        for element in os.listdir(self.anim_dir+'/'+self.show_dir+'/'):
            directory = self.anim_dir+'/'+self.show_dir+'/'+element
            the_shows.append(element)
            the_shows_dict[element] = directory
            counter += 1
            logger.trace('  -> ' + str(counter) + ' ' + str(element) + '=' + str(directory))
        self.the_shows['the_shows'] = the_shows
        self.the_shows['the_shows_dict'] = the_shows_dict
        self.the_shows['max_show_number'] = counter
        self.max_show_number = counter
        #
        # fill the list of pauses
        #
        counter = 0
        the_shows = []
        the_shows_dict = {}
        logger.debug('init pause shows')
        for element in os.listdir(self.anim_dir+'/'+self.pause_dir+'/'):
            directory = self.anim_dir+'/'+self.pause_dir+'/'+element
            the_shows.append(element)
            the_shows_dict[element] = directory
            counter += 1
            logger.trace('  -> ' + str(counter) + ' ' + str(element) + '=' + str(directory))
        self.the_shows['the_pauses'] = the_shows
        self.the_shows['the_pauses_dict'] = the_shows_dict
        self.the_shows['max_pause_show_number'] = counter
        self.max_pause_show_number = counter
        #
        # fill the list of after shows
        #
        counter = 0
        the_shows = []
        the_shows_dict = {}
        logger.debug('init after shows')
        for element in os.listdir(self.anim_dir+'/'+self.after_dir+'/'):
            directory = self.anim_dir+'/'+self.after_dir+'/'+element
            the_shows.append(element)
            the_shows_dict[element] = directory
            counter += 1
            logger.trace('  -> ' + str(counter) + ' ' + str(element) + '=' + str(directory))
        self.the_shows['the_afters'] = the_shows
        self.the_shows['the_afters_dict'] = the_shows_dict
        self.the_shows['max_after_show_number'] = counter
        self.max_after_show_number = counter
    
    #
    #  TEXT FUNCTIONS
    #
    def showDateTimeOrCountDown(self, d_or_c='d'):
        #async def showDateTimeOrCountDown(self, d_or_c='d'):
        if self.use_display == True:
            show_text = []
            #
            #  SHOW DATE AND TIME
            #  after the intro of a pause show, we may show the time and date
            #
            if d_or_c == 'd' or d_or_c == 'b':
                logger.debug('Displaying the date time')
                
                weekday, datum, uhrzeit = self.clock.getDateTime()
                show_text.append(uhrzeit)
                show_text.append(weekday)
                show_text.append(datum)
                
                logger.trace(show_text)
            #
            #  SHOW DAYS UNTIL THE COUNTDOWN DATE
            #  before showing the before show text, we may show the days until countdown
            #
            if d_or_c == 'c' or d_or_c == 'b':
                logger.debug('Displaying the countdown text')
                
                show_text.append('Noch ' + str(self.clock.countdown()) + ' Tage')
                if d_or_c == 'c':
                    show_text.append('bis')
                    show_text.append(self.target_event)
                
                logger.trace(show_text)
            
            #asyncio.run(self.showText(show_text, True, True, self.sleep_after_date_time_line, self.sleep_after_date_time_show))
            self.showText(show_text, True, True, self.sleep_after_date_time_line, self.sleep_after_date_time_show)
            
            self.fillScreen(0)
    
    #
    # CREATE THE after_the_show_text TEXT
    #
    def getBeforeOrAftershowText(self, is_after_text=False):
        if is_after_text == True:
            greeting_number = random.randint(self.min_after_the_show_text_number,self.max_after_text_show_number)
            greetings = self.after_the_show_text_greeting_text
            number_of_text_elements_to_show = self.after_the_show_text_to_show
        else:
            greeting_number = random.randint(self.min_before_the_show_text_number,self.max_before_the_show_text_number)
            greetings = self.before_the_show_text_greeting_text
            number_of_text_elements_to_show = self.before_the_show_text_number_to_show
        
        logger.trace('greeting text number '+str(greeting_number)+' selected')
        greeting = greetings.get(greeting_number)
        
        # get the after_the_show_text 
        text = []
        for element in greeting:
            text.append(element)
        
        text_element_numbers = []
        i = 0
        max_after_the_show_text_elements = len(self.after_the_show_text_text)-1
        max_before_the_show_text_elements = len(self.before_the_show_text_text)-1
        
        while i < number_of_text_elements_to_show:
            if is_after_text == True:
                text_element_number = random.randint(0,max_after_the_show_text_elements)
            else:
                text_element_number = random.randint(0,max_before_the_show_text_elements)
                
            if text_element_number in text_element_numbers:
                else_is_false = False
            else:
                text_element_numbers.append(text_element_number)
                if is_after_text == True:
                    text.append(self.setup.getElementFromArray('after_the_show_text_text', text_element_number))
                else:
                    text.append(self.setup.getElementFromArray('before_the_show_text_text', text_element_number))
                i += 1
        
        text.append('Danke Dir')
        
        return(text)
    
    #
    #  DISPLAY TEXT ON THE OLED
    #
    async def showText(self, array=[], x_centered=True, y_centered=False, text_pause=250, sleep_after_text=1000):
        y_pos = 0
        x_pos = 0
        height = 0
        num_lines = 0
        
        # in case we want to vertically center the text
        # we need to get the number of lines in the array
        for element in array:
            num_lines += 1
        height = num_lines*12
        
        logger.trace('text: ' + str(array) + ' has ' + str(num_lines) + ' lines that take up ' + str(num_lines*self.increment) + 'px')
        if (height) > self.max_text_height:
            logger.crazy(str(num_lines) + ' lines (with '+str(num_lines*self.increment)+'px) is more than fits on one screen, turning off y_centered')
            y_centered = False
        
        counter = 0
        for element in array:
            # get the height and width position on which to start the text
            if y_centered == True:
                # in case we want the text to be horizontally centered, we need to determine the px to start
                y_pos = int(((self.oled_height - num_lines*self.increment) + counter*(self.increment*2)) / 2 ) # vertical
            else:
                # if not, we just need to make sure, that we do not print text after 60 px (wont fit)
                if y_pos >= self.max_text_height: # 60
                    y_pos = 0
                    self.fillScreen(0)
            if x_centered == True:
                x_pos = int((self.oled_width - len(element)*self.character_width) / 2) # horizontal
            else:
                # the wishlist eg. is simply displayed 1 px from the left
                x_pos = 1
            
            logger.crazy('text: ' + str(element) + ' x:' + str(x_pos) + ' y:' + str(y_pos))
            if self.use_display == True:
                self.oled.text(element, x_pos, y_pos)
            
            if y_centered == False:
                y_pos += self.increment
            
            if self.use_display == True:
                self.oled.show() # show the text
            counter += 1
            
            await asyncio.sleep_ms(text_pause)
            
        await asyncio.sleep_ms(sleep_after_text)
        
    #
    # SHOW A SERIES OF IMAGES USING THE LOW LEVEL IMAGE FUNCTIONS
    #
    async def showImageSequence(self, directory, invert_color, image_pause, repetitions, sleep_after_animation):
        run = 0
        while run < repetitions:
            # get all the files of the image animation from the directory
            image_sequence = os.listdir(directory)
            
            # now loop trough this array to get the image as a bytearray and feed it into the display function
            for img in image_sequence:
                logger.crazy('suffix of file is ' +str(img) + ' is ' +str( img[len(img)-3:len(img)]))
                if img[len(img)-3:len(img)] == 'pbm':
                    file = directory+'/'+img
                    img_width, img_height, skip_lines = self.getImageDimension(file)
                    x_pos = (self.oled_width  - img_width) / 2
                    y_pos = (self.oled_height - img_height) / 2
                    
                    logger.crazy('display image ' + str(file) + ' run ' + str(run) + ' w=' + str(img_width) + ' / h=' + str(img_height) + ' at x=' + str(x_pos) + ' / y=' + str(y_pos) + ' skip ' + str(skip_lines) + ' lines of file')
                    
                    self.showImage(self.getImageBuffer(file, skip_lines), int(img_width), int(img_height), int(x_pos), int(y_pos))
                    await asyncio.sleep_ms(image_pause)
                
            run += 1
            
        logger.crazy('image sequence for directory ' + str(directory) + ' done sleeping for ' + str(sleep_after_animation))
        await asyncio.sleep_ms(sleep_after_animation)
        
    def invertScreen(self, color):
        logger.crazy('invert screen with ' + str(color))
        if self.use_display == True:
            self.oled.invert(color)
    def fillScreen(self, color):
        logger.crazy('fill screen with ' + str(color))
        if self.use_display == True:
            self.oled.fill(color)
    def blankScreen(self):
        logger.crazy('blank screen')
        if self.use_display == True:
            self.oled.fill(0)
    def getImageDimension(self, file_to_check):
        with open(file_to_check, 'r') as f:
            f.readline()
            skip_line = 0
            while skip_line < 2:
                skip_line += 1
                Content = f.readline()
                if Content[0] != '#':
                    position = int(Content.find(' '))
                    length = len(Content)
                    if int(position) > 0:
                        img_width = int(Content[0:int(position)])
                        img_height = int(Content[int(position)+1:length])
                        return(img_width, img_height, skip_line+1)
                    else:
                        logger.error('ERROR - COULD NOT GET IMAGE DIMENSIONS')
                        return(128, 64, skip_line+1)
    def getImageBuffer(self, file_to_show='anim/show/sboat/00.pbm', skip_lines=2):
        with open(file_to_show, 'rb') as f:
            line = 0
            while line < skip_lines:
                f.readline() # The first 2-3 lines of PBM files are pure info
                line += 1
            byte_array=bytearray(f.read())
        return(byte_array)
    def showImage(self, img_buffer, img_width, img_height, x_pos, y_pos):
        if self.use_display == True:
            data = framebuf.FrameBuffer(img_buffer, img_width, img_height, framebuf.MONO_HLSB)
            self.oled.blit(data, x_pos, y_pos)
            self.oled.show()
