import logging
from time import sleep
LOG = logging.getLogger('uarm-mock')


class SwiftAPI(object):
    def __init__(self, filters={'hwid': 'USB VID:PID=2341:0042'}, callback_thread_pool_size=1):
        pass

    def set_pump(self, *args, on, **kwargs):
        return "OK"

    def waiting_ready(self):
        pass

    def set_position(self, *args, **kwargs):
        return "OK"
