"Some utilities functions"

import calendar
import time
from Settings import Settings

def split_path_and_file(path):
    "Returns the given path and file name as a tuple, (dir_path, file_name)"
    if '/' in path:
        if '.' in path and path not in ['.', '..'] :
            last_index = path.rfind('/')
            dir_path = path[:last_index]
            file_name = path[last_index + 1:]
        else:
            dir_path = path
            file_name = None
        print 'Dir: {0}, file:{1}'.format(dir_path, file_name)
        return (dir_path, file_name)
    return ('.', file_name)

def get_cluster_offset(block_id):
        '''
        Returns the Cluster offset in the whole storage device.
        '''
        return Settings.datablock_region_offset + (block_id * Settings.datablock_size)

def get_current_time_seconds():
    '''
    Returns the unix time
    '''
    return calendar.timegm(time.gmtime())