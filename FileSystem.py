# -*- coding: utf-8 -*-
'''
Author: Cesar Bonilla
Module to Handle the Ext2 File System
'''

import struct
from bitarray import bitarray
from InodeBase import Inode
from ClusterTable import ClusterTable
from InodeTable import InodeTable
from Settings import Settings

class FileSystem(object):
    '''
    Class to Handle the Basic File system Operations as read, write, delete
    and create files. All size properties are in bytes.
    '''

    def __init__(self, fs_file):
        self.file_object = fs_file
        self.working_dir = "/"

    def _create_file_system(self):
        "Create a new ext2 file with the default structure"
        print "Allocating new file system at '{0}'".format(self.file_object)
        self.__allocate_bitmap(Settings.datablock_bitmap_size)
        self.__allocate_bitmap(Settings.inode_bitmap_size)
        self.__create_inode_table(Settings.inode_max_elements)
        self.__allocate_space(Settings.datablock_region_size)
        self.__create_root_inode()
        print "File system allocated"

    def __allocate_space(self, size):
        '''
        Allocates a space of "size" bytes in the current file.
        '''
        chunk = "a"*size
        self.file_object.write(chunk)

    def __allocate_bitmap(self, size):
        '''
        Creates a bitmap where all the bits are set to 1 and writes it to the current file.
        '''
        array = bitarray(size*8)
        array.setall(True)
        self.file_object.write(array.tobytes())
        

    def __create_inode_table(self, table_len):
        '''
        Creates "table_len" Inodes into the current file.
        '''
        while table_len > 1:
            inode = Inode()
            self.file_object.write(inode.to_binary())
            table_len = table_len-1

    def __create_root_inode(self):
        '''
        Sets the Inode & Block 0 as occupied and updates the root inode block.
        '''
        InodeTable.set_inode_as_occupied(0, self.file_object)
        ClusterTable.set_cluster_as_occupied(0, self.file_object)
        root_inode = InodeTable.get_root_inode(self.file_object)
        print "Root Inode cri: {0}".format(root_inode)
        
        #Creating dir entry
        print "Allocating first block for root inode"
        root_inode.i_size += self.__add_dir_entry("/", 0)
        InodeTable.set_inode(0, root_inode, self.file_object)
        print "Allocated"

    def __add_dir_entry(self, dir_entry_name, inode_id):
        '''
        Adds a new dir entry at the current directory and returns the dir entry size
        '''
        struct_mask = 'ii{0}s'.format(len(dir_entry_name))
        dir_entry_size = struct.calcsize(struct_mask)
        block_data = struct.pack(struct_mask, dir_entry_size, inode_id, dir_entry_name)
        self.file_object.seek(Settings.datablock_region_offset)
        self.file_object.seek(Settings.inode_size * inode_id, 1)
        self.file_object.write(block_data)
        return dir_entry_size

    def create_file(self, file_name):
        '''
        Creates a new file and return the assigned Inode ID
        '''
        inode_id = -1
        InodeTable.get_free_inode_index(self.file_object)
        return inode_id



    @classmethod
    def bits(cls, f):
        bytes = (ord(b) for b in f.read())
        for b in bytes:
            for i in xrange(8):
                yield (b >> i) & 1
        