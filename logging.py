import time

class getLogger:
    SEVERITY = {
        'CRITICAL': 0
        , 'ERROR': 5
        , 'WARNING': 10
        , 'INFO': 20
        , 'DEBUG': 30
        , 'TRACE': 40
        , 'CRAZY': 50
        }
    
    def __init__(self, NAME, LEVEL=0):
        self.LOG_NAME = NAME
        self.LOG_LEVEL = LEVEL
    
    def setLevel(self, LEVEL):
        self.LOG_LEVEL = self.SEVERITY.get(LEVEL)
    
    def getTime(self):
        cur_time = time.localtime()
        year = str(cur_time[0])
        month = str(cur_time[1])
        day = str(cur_time[2])
        hour = str(cur_time[3])
        minute = str(cur_time[4])
        second = str(cur_time[5])
        
        if len(day) == 1:
            day = '0'+day
        if len(month) == 1:
            month = '0'+month
        if len(hour) == 1:
            hour = '0'+hour
        if len(minute) == 1:
            minute = '0'+minute
        if len(second) == 1:
            second = '0'+second
        
        return (str(day)+'.'+str(month)+'.'+str(year)+' '+str(hour)+':'+str(minute)+':'+str(second))
        #return (str(hour.zfill(2))+':'+str(minute)+':'+str(second))
    
    # print out log messages ONLY if loglevel is equal or greater to secerity
    def critical(self, message):
        if self.LOG_LEVEL >= self.SEVERITY.get('CRITICAL'):
            print(self.getTime()+' ' + self.LOG_NAME + ' (CRITICAL): ' + message)
    def error(self, message):
        if self.LOG_LEVEL >= self.SEVERITY.get('ERROR'):
            print(self.getTime()+' ' + self.LOG_NAME + ' (ERROR): ' + message)
    def warning(self, message):
        if self.LOG_LEVEL >= self.SEVERITY.get('WARNING'):
            print(self.getTime()+' ' + self.LOG_NAME + ' (WARNING): ' + message)
    def info(self, message):
        if self.LOG_LEVEL >= self.SEVERITY.get('INFO'):
            print(self.getTime()+' ' + self.LOG_NAME + ' (INFO): ' + message)
    def debug(self, message):
        if self.LOG_LEVEL >= self.SEVERITY.get('DEBUG'):
            print(self.getTime()+' ' + self.LOG_NAME + ' (DEBUG): ' + message)
    def trace(self, message):
        if self.LOG_LEVEL >= self.SEVERITY.get('TRACE'):
            print(self.getTime()+' ' + self.LOG_NAME + ' (TRACE): ' + message)
    def crazy(self, message):
        if self.LOG_LEVEL >= self.SEVERITY.get('CRAZY'):
            print(self.getTime()+' ' + self.LOG_NAME + ' (CRAZY): ' + message)
    