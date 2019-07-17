import logging
from time import time

class WAM_Logger:# timestamp
    def __init__(self):
        self.timestamp = str(time())
        self.logger = logging.getLogger('BDM-WAM ' + self.timestamp)
        if not len(self.logger.handlers):
            self.logger.setLevel(logging.DEBUG)
            self.fh = logging.FileHandler('BDM-WAM ' + self.timestamp + '.log')
            self.fh.setLevel(logging.DEBUG)

            # create console handler with a higher log level
            self.ch = logging.StreamHandler()
            self.ch.setLevel(logging.ERROR)

            # create formatter and add it to the handlers
            self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            self.fh.setFormatter(self.formatter)
            self.ch.setFormatter(self.formatter)

        # add the handlers to the logger
            self.logger.addHandler(self.fh)
            self.logger.addHandler(self.ch)

    def log_it(self, event):
        try:
            self.logger.info(event)
        except:
            self.logger.info('Log Failure')

    def log_end(self):
        self.logger.info('************* HAPPY ANALYSING... LOG COMPLETE!!! ************* ')
        logging.shutdown()
        self.fh.close()
        self.ch.close()