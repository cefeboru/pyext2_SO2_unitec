# -*- coding: utf-8 -*-
"Module to Handle the Ext2 File System"

import os.path
from bitarray import bitarray
from InodeBase import Inode
from InodeTable import InodeTable

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
        self.datablock_region_size = self.datablock_size * self.datablock_max_elements
        self.inode_size = 54
        self.inode_max_elements = 1024
        self.inode_bitmap_size = self.inode_max_elements / 8
        self.inode_bitmap_offset = self.datablock_bitmap_size - 1
        self.inode_table_size = self.inode_max_elements * self.inode_size
        self.inode_table_offset = self.inode_bitmap_offset + self.inode_bitmap_size

        if os.path.isfile(filesystem_path):
            print "Loading root inode"
            with open(self.filesystem_path, mode = 'r+b') as fs_file:
                InodeTable.set_offset(self.inode_table_offset)
                root_inode = InodeTable.get_root_inode(fs_file)
                print "Root Created at {0}".format(root_inode.i_cdate)
        else:
            print "File system not found!"
            print "Creating file system in file {0}".format(self.filesystem_path)
            self._create_file_system(self.filesystem_path)

    def _create_file_system(self, file_path=None):
        "Create a new ext2 file with the default structure"
        if file_path is not None:
            self.filesystem_path = file_path
        with open(self.filesystem_path, mode='wb') as file_object:
            self.__create_cluster_bitmap(self.datablock_max_elements, file_object)
            self.__create_inode_bitmap(self.inode_max_elements, file_object)
            self.__create_inode_table(self.inode_max_elements, file_object)
            #self.__create_cluster_region(self.datablock_region_size, file_object)

    @classmethod
    def __create_inode_table(cls, size, file_object):
        for i in xrange(size):
            file_object.write(Inode().to_binary())

    @classmethod
    def __create_inode_bitmap(cls, size, file_object):
        inode_bitmap = bitarray()
        inode_bitmap.append(False) # Root inode
        for i in xrange(size-1):
            inode_bitmap.append(True)
        file_object.write(inode_bitmap)

    @classmethod
    def __create_cluster_bitmap(cls, size, file_object):
        datablock_bitmap = bitarray()
        for i in xrange(size):
            datablock_bitmap.append(True)
        file_object.write(datablock_bitmap)

    @classmethod
    def __create_cluster_region(cls, size, file_object):
        chunk = "a"*size
        file_object.write(chunk)

    def open_file(self, file_name):
        #TODO - READ INODE
        # - READ BLOCKS
        # - GET DATA FROM DATA REGION
        pass

    def __get_root_inode(self, inode_number, file_object):
        inode_table_offset = self.inode_table_offset


    @classmethod
    def bits(cls, f):
        bytes = (ord(b) for b in f.read())
        for b in bytes:
            for i in xrange(8):
                yield (b >> i) & 1

fs_instance = FileSystem("FS.ext2")
        