# -*- coding: utf-8 -*-
"Module to Handle the Ext2 File System"

import os.path
from bitarray import bitarray
from InodeBase import Inode
from InodeTable import InodeTable
from Settings import Settings

class FileSystem(object):
    '''
    Class to Handle the Basic File system Operations as read, write, delete
    and create files. All size properties are in bytes.
    '''

    def __init__(self, filesystem_path):
        self.filesystem_path = filesystem_path
        Settings.datablock_bitmap_size = Settings.datablock_max_elements / 8
        Settings.datablock_region_size = Settings.datablock_size * Settings.datablock_max_elements
        Settings.inode_bitmap_size = Settings.inode_max_elements / 8
        Settings.inode_bitmap_offset = Settings.datablock_bitmap_size
        Settings.inode_table_size = Settings.inode_max_elements * Settings.inode_size
        Settings.inode_table_offset = Settings.inode_bitmap_offset + Settings.inode_bitmap_size

        if os.path.isfile(filesystem_path):
            print "Loading root inode"
            with open(self.filesystem_path, mode = 'r+b') as fs_file:
                fs_file.seek(Settings.inode_table_offset)
                root_inode = InodeTable.get_inode(1, fs_file)
                print root_inode
                print "Root Created at {0}".format(root_inode.i_cdate)
        else:
            print "File system not found, please allocate the file system file first!"

    def _create_file_system(self, file_path=None):
        "Create a new ext2 file with the default structure"
        if file_path is not None:
            self.filesystem_path = file_path
        with open(self.filesystem_path, mode='wb') as file_object:
            self.__allocate_bitmap(Settings.datablock_bitmap_size, file_object)
            self.__allocate_bitmap(Settings.inode_bitmap_size, file_object)
            self.__create_inode_table(Settings.inode_max_elements, file_object)
            self.__allocate_space(Settings.datablock_region_size, file_object)

    @classmethod
    def __allocate_space(cls, size, file_object):
        chunk = "a"*size
        file_object.write(chunk)

    @classmethod
    def __allocate_bitmap(cls, size, file_object):
        for i in xrange(size):
            file_object.write(bitarray("1"*8).tobytes())
        

    @classmethod
    def __create_inode_table(cls, table_len, file_object):
        while table_len > 1:
            inode = Inode()
            file_object.write(inode.to_binary())
            table_len = table_len-1

    def open_file(self, file_name):
        #TODO - READ INODE
        # - READ BLOCKS
        # - GET DATA FROM DATA REGION
        pass

    @classmethod
    def bits(cls, f):
        bytes = (ord(b) for b in f.read())
        for b in bytes:
            for i in xrange(8):
                yield (b >> i) & 1
        