'''
Author: Cesar Bonilla
Module to handle all the Inode Table Operations
'''
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
        file_object.seek(Settings.inode_table_offset)
        inode_offset = inode_id * Settings.inode_size
        file_object.seek(inode_offset, 1)
        i_bytes = file_object.read(Settings.inode_size)
        inode = Inode().from_binary(i_bytes)
        return inode

    @classmethod
    def get_free_inode_index(cls, file_object):
        '''
        Reads and return the first inode element that is free
        '''
        file_object.seek(Settings.inode_bitmap_offset)
        bitmap_bytes = file_object.read(Settings.inode_bitmap_size)
        data = bitarray()
        data.frombytes(bitmap_bytes)
        try:
            free_inode_position = data.index(True)
            return free_inode_position
        except ValueError:
            raise ValueError("No more free Inodes, please delete some files")

    @classmethod
    def set_inode_as_occupied(cls, inode_id, file_object):
        '''
        Stablish the inode as occupied, will set the bit to 0 in the bitmap
        '''
        file_object.seek(Settings.inode_bitmap_offset)
        bitmap_bytes = file_object.read(Settings.inode_bitmap_size)
        data = bitarray()
        data.frombytes(bitmap_bytes)
        try:
            data[inode_id] = 0
            marked_inode = data[inode_id]
            return marked_inode
        except ValueError:
            raise ValueError("Unable to set inode as occupied")
       
        