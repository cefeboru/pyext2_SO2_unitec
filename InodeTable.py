"Module to handle all the Inode Table Operations"

from InodeBase import Inode
import struct

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
    def set_offset(cls, offset):
        '''
        Sets the table offset in bytes in the filesystem object
        '''
        cls._offset = offset