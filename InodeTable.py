"Module to handle all the Inode Table Operations"
import struct
from InodeBase import Inode
from Settings import Settings
from bitarray import bitarray

class InodeTable(object):
    "Inode Table API to perform Read & Write Operations"
    @classmethod
    def get_root_inode(cls, file_object):
        '''
        Get Inode at position 0
        '''
        binary_inode = file_object.read(Settings.inode_size)
        inode = Inode().from_binary(binary_inode)
        return inode

    @classmethod
    def get_inode(cls, inode_id, file_object):
        '''
        Read the Inode with the specified id
        '''
        offset = inode_id * Settings.inode_size
        file_object.seek(offset, 1)
        i_bytes = file_object.read(Settings.inode_size)
        inode = Inode().from_binary(i_bytes)
        return inode

    @classmethod
    def get_first_free_inode(cls, file_object):
        '''
        Reads and return the first inode element that us unused
        '''
        bitmap_bytes = file_object.read(Settings.inode_bitmap_size)
        print "Inode Bitmap"
        data = bitarray()
        data.frombytes(bitmap_bytes)
        try:
            free_inode_position = data.index(True)
            return free_inode_position
        except ValueError:
            raise ValueError("No more free Inodes, please delete some files")
