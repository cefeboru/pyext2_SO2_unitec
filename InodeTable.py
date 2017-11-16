"Module to handle all the Inode Table Operations"
import struct
from InodeBase import Inode
from Settings import Settings

class InodeTable(object):
    "Inode Table API to perform Read & Write Operations"
    @classmethod
    def get_root_inode(cls, file_object):
        '''
        Get Inode at position 0
        '''
        size = struct.calcsize(Inode._i_struct)
        binary_inode = file_object.read(size)
        inode = Inode().from_binary(binary_inode)
        return inode

    @classmethod
    def get_inode(cls, inode_id, file_object):
        '''
        Read the Inode with the specified id
        '''
        size = struct.calcsize(Inode._i_struct)
        offset = inode_id * size
        file_object.seek(offset, 1)
        i_bytes = file_object.read(size)
        inode = Inode().from_binary(i_bytes)
        return inode

    @classmethod
    def get_first_free_inode(cls, file_object):
        '''
        Reads and return the first inode element that us unused
        '''
        bitmap_bytes = file_object.read(Settings.inode_bitmap_size)

    @classmethod
    def set_offset(cls, offset):
        '''
        Sets the table offset in bytes in the filesystem object
        '''
        cls._offset = offset
        return None
