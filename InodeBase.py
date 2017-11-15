"Base Inode Structure"
import calendar
import time
import struct
from bitarray import bitarray


class Inode(object):
    '''
    Base Metadata Structure of an inode:
    Mode, File Size, Created Date, Accesed Date, Deleted Date
    '''
    _i_struct = 'iillllhhhhhhhhhhhhhhh'
    i_struct_size = struct.calcsize(_i_struct)

    def __init__(self):
        self.i_mode = -1
        self.i_size = 0
        self.i_cdate = calendar.timegm(time.gmtime())
        self.i_adate = 0
        self.i_mdate = calendar.timegm(time.gmtime())
        self.i_ddate = 0
        self.i_blocks = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def is_file(self):
        # TODO
        return False

    def is_directyory(self):
        # TODO
        return False

    def is_socket(self):
        # TODO
        return False

    def to_binary(self):
        "Convert currents instance to bytes using struct.pack"
        return struct.pack(Inode._i_struct, self.i_mode, self.i_size, self.i_cdate,
                           self.i_adate, self.i_mdate, self.i_ddate, self.i_blocks[0],
                           self.i_blocks[1], self.i_blocks[2], self.i_blocks[3], self.i_blocks[4],
                           self.i_blocks[5], self.i_blocks[6], self.i_blocks[7], self.i_blocks[8],
                           self.i_blocks[9], self.i_blocks[10], self.i_blocks[11], self.i_blocks[12],
                           self.i_blocks[13], self.i_blocks[14])

    def from_binary(self, file_object):
        "Load struct data from buffer and returns the Inode"
        binary_inode = file_object.read(struct.calcsize(self._i_struct))
        unpacked_data = struct.unpack(self._i_struct, binary_inode)
        self.i_mode = unpacked_data[0]
        self.i_size = unpacked_data[1]
        self.i_cdate = unpacked_data[2]
        self.i_adate = unpacked_data[3]
        self.i_mdate = unpacked_data[4]
        self.i_ddate = unpacked_data[5]
        self.i_blocks[0] = unpacked_data[6]
        return self

class Bitmap(object):
    def __init__(self, bitmap_size):
        self.size = bitmap_size
        self._bitmap = bitarray('1'*bitmap_size)

    def from_bytes(self, bytes):
        self._bitmap = bitarray(bytes)
