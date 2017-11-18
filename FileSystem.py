# -*- coding: utf-8 -*-
'''
Author: Cesar Bonilla
Module to Handle the Ext2 File System
'''

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

    def __init__(self, fs_file):
        self.file_object = fs_file

    def _create_file_system(self):
        "Create a new ext2 file with the default structure"
        print "Allocating new file system at '{0}'".format(self.file_object)
        self.__allocate_bitmap(Settings.datablock_bitmap_size, self.file_object)
        self.__allocate_bitmap(Settings.inode_bitmap_size, self.file_object)
        self.__create_inode_table(Settings.inode_max_elements, self.file_object)
        self.__allocate_space(Settings.datablock_region_size, self.file_object)
        print "File system allocated"

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
        