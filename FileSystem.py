# -*- coding: utf-8 -*-
"Module to Handle the Ext2 File System"

import os.path
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
        self.inode_size = Inode.i_struct_size
        self.inode_max_elements = 1024
        self.inode_bitmap_size = self.inode_max_elements / 8
        self.inode_bitmap_offset = self.datablock_bitmap_size
        self.inode_table_size = self.inode_max_elements * self.inode_size
        self.inode_table_offset = self.inode_bitmap_offset + self.inode_bitmap_size

        if os.path.isfile(filesystem_path):
            print "Loading root inode"
            with open(self.filesystem_path, mode = 'r+b') as fs_file:
                fs_file.seek(self.inode_table_offset)
                root_inode = InodeTable.get_inode(1, fs_file)
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
            self.__allocate_space(self.datablock_bitmap_size, file_object)
            self.__allocate_space(self.inode_bitmap_size, file_object)
            self.__create_inode_table(self.inode_max_elements, file_object)
            self.__allocate_space(self.datablock_region_size, file_object)

    @classmethod
    def __allocate_space(cls, size, file_object):
        chunk = bytearray(size)
        file_object.write(chunk)

    @classmethod
    def __create_inode_table(cls, len, file_object):
        while len > 1:
            inode = Inode()
            file_object.write(inode.to_binary())
            len = len-1

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

fs_instance = FileSystem("FS.ext2")
        