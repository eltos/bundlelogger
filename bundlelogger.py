# Copyright 2017 Philipp Niedermayer (github.com/eltos)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from logging import Logger, LogRecord, DEBUG, INFO, WARNING, ERROR, CRITICAL, NOTSET
from threading import Timer
from math import log10
from copy import copy


class BundleLogger(Logger):
    """
    A logger that bundles frequently reoccuring messages.
    
    Possible output may look like this:
        14,746 INFO: 1234 errors following, long delay after #204
        14,747 ERROR: fail
        14,762 ERROR: fail
        14,775 ERROR: fail
        14,789 ERROR: fail
        14,803 ERROR: fail
        14,875 ERROR: [10 repetitions] fail
        15,076 ERROR: [20 repetitions] fail
        15,505 ERROR: [50 repetitions] fail
        16,280 ERROR: [100 repetitions] fail
        17,723 ERROR: [200 repetitions] fail
        17,813 ERROR: [204 repetitions] fail
        37,073 ERROR: [500 repetitions] fail
        44,127 ERROR: [1000 repetitions] fail
        47,466 ERROR: [1234 repetitions] fail
        47,480 INFO: Test completed
    """
    
    def __init__(self, name, level=NOTSET, maxDelay=10*60, minRepetitions=5):
        """
        Initialize the logger with the given name and level.
        
        Use maxDelay to specify the number of seconds to wait for the next
            repetition of a log message
        Use minRepetitions to specify the minimum number of consecutive
            messages that are considered repetitions
        
        """
        Logger.__init__(self, name, level)
        
        self.minRepetitions = minRepetitions  # default: 5
        self.maxDelay = maxDelay  # default: 10min (use 0 to disable)
        
        self.savedRecord = None
        self.count = 0
        self.lastLogCount = 0
        self.timer = Timer(0, lambda:None)
    
    def setMaxDelay(self, maxDelay):
        """
        Specify the number of seconds to wait for the next repetition of a log message
        """
        self.maxDelay = maxDelay
    
    def setMinRepetitions(self, minRepetitions):
        """
        Specify the minimum number of consecutive messages that are considered repetitions
        """
        self.minRepetitions = minRepetitions
    
    def equalsSaved(self, record):
        return self.savedRecord is not None and \
               isinstance(record, LogRecord) and \
               record.levelno == self.savedRecord.levelno and \
               record.getMessage() == self.savedRecord.getMessage()
    
    def logSavedRecord(self):
        self.bundleAndCallHandlers(self.savedRecord)
    
    def bundleAndCallHandlers(self, record):
        bundleRecord = copy(record)
        bundleRecord.msg = "[%i repetitions] %s"%(self.count, bundleRecord.msg)
        self.lastLogCount = self.count
        self.callHandlers(bundleRecord)
    
    def handle(self, record):
        """
        Call the handlers for the specified record.
        
        This method is used for unpickled records received from a socket, as
        well as those created locally. Logger-level filtering is applied.
        """
        if (not self.disabled) and self.filter(record):
            self.timer.cancel()
            
            if self.equalsSaved(record):
                self.count += 1
                
                n = int(log10(self.count))
                
                if self.count <= self.minRepetitions:
                    # log first x repetions as single entries
                    self.lastLogCount = self.count
                    self.callHandlers(record)
                    
                elif self.count in [10**n, 2*10**n, 5*10**n]:
                    # at 1, 2, 5, 10, 20, 50, 100, 200, 500, ...
                    self.bundleAndCallHandlers(record)
                    
                elif self.maxDelay > 0:
                    self.timer = Timer(self.maxDelay, self.logSavedRecord)
                    self.timer.start()
                
            else:
                if self.lastLogCount < self.count:
                    self.logSavedRecord()
                
                self.count = 1
                self.lastLogCount = 1
                self.callHandlers(record)
            
            
            self.savedRecord = record  # save most recent record
            



if __name__ == '__main__':
    import logging, logging.handlers, time
    
    
    logging.Logger.manager.setLoggerClass(BundleLogger)
    
    
    print("DEMO will create a log file 'log.log'")
    
    # Log file
    fh = logging.handlers.RotatingFileHandler('log.log', maxBytes=1024*1024, backupCount=5)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter(
        '%(asctime)s %(name)s %(levelname)s: %(message)s'))
    logging.getLogger().addHandler(fh)
    # Console log
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)  # INFO DEBUG
    logging.getLogger().addHandler(ch)
    
    
    # Logger
    LOG = logging.getLogger("logger#564")
    LOG.setLevel(logging.DEBUG)
    
    
    LOG.setMaxDelay(2)  # in any case, log after 2s without any new log msgs
    
    
    
    # Test
    LOG.info("This is a test.")
    LOG.debug("debug example")
    LOG.critical("critical example")
    LOG.info("1234 errors following...")
    for i in range(204):
        LOG.error("fail")
        time.sleep(0.01)
    print("so many fails, I need 5 sec break...")
    time.sleep(5)
    print("ok, time to fail a few more times...")
    for i in range(1030):
        LOG.error("fail")
        time.sleep(0.01)
    
    LOG.info("Test completed")
