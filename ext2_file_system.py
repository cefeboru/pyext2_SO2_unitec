"Module to Handle the Ext2 File System"

import os.path
from bitarray import bitarray
from Inode import InodeBase

class FileSystem(object):
    '''
    Class to Handle the Basic File system Operations, all sizes are in bytes.
    '''

    def __init__(self, filesystem_path):
        self.filesystem_path = filesystem_path
        self.filesystem_buffer = None
        self.datablock_size = 4096
        self.datablock_max_elements = 65536
        self.datablock_bitmap_size = self.datablock_max_elements / 8
        self.datablock_bitmap_offset = 0
        self.inode_size = 64
        self.inode_max_elements = 1024
        self.inode_bitmap_size = self.inode_max_elements / 8
        self.inode_bitmap_offset = self.datablock_bitmap_size - 1
        self.inode_table_size = self.inode_max_elements * self.inode_size
        self.inode_table_offset = self.inode_bitmap_offset + self.inode_bitmap_size
        self.datablock_region_size = self.datablock_size * self.datablock_max_elements
        self.inode_table = []

        if os.path.isfile(filesystem_path):
            print "The File System exists!!"
        else:
            print "File System must be created!!"

    def create_new_file_system(self, file_path):
        "Create a new ext2 file with the default structure"
        self.filesystem_path = file_path
        inode_bitmap = self.create_new_inode_bitmap(self.inode_max_elements)
        inode_table = self.create_new_inode_table(self.inode_max_elements)
        #TODO SOME MAGIC

    def create_new_inode_table(self, size):
        table = list()
        for i in range(0, size):
            inode = InodeBase.Inode()
            table.append(inode)
        return table

    def create_new_inode_bitmap(self, size):
        inode_bitmap = bitarray()
        for i in range(0, size):
            inode_bitmap.append(True)
        return inode_bitmap

