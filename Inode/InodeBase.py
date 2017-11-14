"Base Inode Structures"
import calendar
import time

class Inode(object):
    '''
    Base Metadata Structure of an inode:
    Mode, File Size, Created Date, Accesed Date, Deleted Date
    '''
    def __init__(self):
        self.i_mode = -1
        self.i_size = 0
        self.i_cdate = calendar.timegm(time.gmtime())
        self.i_adate = 0
        self.i_mdate = calendar.timegm(time.gmtime())
        self.i_ddate = 0
        self.i_blocks = []

    def is_file(self):
        return False
    
    def is_directyory(self):
        return False

    def is_socket(self):
        return False
