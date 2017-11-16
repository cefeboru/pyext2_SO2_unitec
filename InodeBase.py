"Base Inode Structure"
import binascii
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
        self.i_mode = 0
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

    def from_binary(self, binary_inode):
        "Load struct data from buffer and returns the Inode"
        unpacked_data = struct.unpack(self._i_struct, binary_inode)
        self.i_mode = unpacked_data[0]
        self.i_size = unpacked_data[1]
        self.i_cdate = unpacked_data[2]
        self.i_adate = unpacked_data[3]
        self.i_mdate = unpacked_data[4]
        self.i_ddate = unpacked_data[5]
        self.i_blocks[0] = unpacked_data[6]
        self.i_blocks[1] = unpacked_data[7]
        self.i_blocks[2] = unpacked_data[8]
        self.i_blocks[3] = unpacked_data[9]
        self.i_blocks[4] = unpacked_data[10]
        self.i_blocks[5] = unpacked_data[11]
        self.i_blocks[6] = unpacked_data[12]
        self.i_blocks[7] = unpacked_data[13]
        self.i_blocks[8] = unpacked_data[14]
        self.i_blocks[9] = unpacked_data[15]
        self.i_blocks[10] = unpacked_data[16]
        self.i_blocks[11] = unpacked_data[17]
        self.i_blocks[12] = unpacked_data[18]
        self.i_blocks[13] = unpacked_data[19]
        self.i_blocks[14] = unpacked_data[20]
        return self

    def __str__(self):
        format_mask = '({0}, {1}, {2}, {3}, {4}, {5} ,{6} ,{7} ,{8}, {9} ,{10} ,{11}, {12}, {13}, {14}, {15}, {16}, {17}, {18}, {19}, {20})'
        return format_mask.format(self.i_mode, self.i_size, self.i_cdate, self.i_adate, self.i_mdate, self.i_ddate, 
                                  self.i_blocks[0], self.i_blocks[1], self.i_blocks[2], self.i_blocks[3], self.i_blocks[4],
                                  self.i_blocks[5], self.i_blocks[6], self.i_blocks[7], self.i_blocks[8], self.i_blocks[9],
                                  self.i_blocks[10], self.i_blocks[11], self.i_blocks[12], self.i_blocks[13], self.i_blocks[14])

