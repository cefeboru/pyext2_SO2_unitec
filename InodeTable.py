'''
Author: Cesar Bonilla
Module to handle all the Inode Table Operations
'''
from InodeBase import Inode
from Settings import Settings
from bitarray import bitarray

class InodeTable(object):
    "Inode Table API to perform Read & Write Operations"

    def __init__(self, file_object):
        self.file_object = file_object

    def get_root_inode(self):
        '''
        Get Inode at position 0
        '''
        self.file_object.seek(Settings.inode_table_offset)
        binary_inode = self.file_object.read(Settings.inode_size)
        inode = Inode().from_binary(binary_inode)
        return inode

    def get_inode(self, inode_id):
        '''
        Read the Inode with the specified id
        '''
        self.file_object.seek(Settings.inode_table_offset)
        inode_offset = inode_id * Settings.inode_size
        self.file_object.seek(inode_offset, 1)
        i_bytes = self.file_object.read(Settings.inode_size)
        inode = Inode().from_binary(i_bytes)
        return inode

    def set_inode(self, index, inode):
        '''
        Writes the inode to the indicated position(inode_id).
        '''
        self.file_object.seek(Settings.inode_table_offset + (Settings.inode_size * index))
        self.file_object.write(inode.to_binary())
        return True

    def get_free_inode_index(self):
        '''
        Reads and return the first inode element that is free
        '''
        self.file_object.seek(Settings.inode_bitmap_offset)
        bitmap_bytes = self.file_object.read(Settings.inode_bitmap_size)
        data = bitarray()
        data.frombytes(bitmap_bytes)
        try:
            free_inode_position = data.index(True)
            return free_inode_position
        except ValueError:
            raise ValueError("No more free Inodes, please delete some files")

    def set_inode_as_occupied(self, inode_id):
        '''
        Stablish the inode as occupied, will set the bit to 0 in the bitmap
        '''
        self.file_object.seek(Settings.inode_bitmap_offset)
        bitmap_bytes = self.file_object.read(Settings.inode_bitmap_size)
        data = bitarray()
        data.frombytes(bitmap_bytes)
        try:
            data[inode_id] = 0
            self.file_object.seek(Settings.inode_bitmap_offset)
            self.file_object.write(data.tobytes())
        except ValueError:
            raise ValueError("Unable to set inode as occupied")
