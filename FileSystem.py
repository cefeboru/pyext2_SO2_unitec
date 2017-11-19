# -*- coding: utf-8 -*-
'''
Author: Cesar Bonilla
Module to Handle the Ext2 File System
'''

import struct
import calendar
import time
import math
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

    def __init__(self, fs_file, create_fs=False):
        self.file_object = fs_file
        self.working_dir = "/"
        self.InodeTable = InodeTable(fs_file)
        self.ClusterTable = ClusterTable(fs_file)
        self.__current_inode_id = 0
        if(not create_fs):
            self.__root_inode = self.InodeTable.get_root_inode()

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
        self.InodeTable.set_inode_as_occupied(0)
        self.ClusterTable.set_cluster_as_occupied(0)
        self.__root_inode = self.InodeTable.get_root_inode()
        self.__current_inode_id = 0
        #TODO ADD CURRENT DIRECTORY "."

    def __add_dir_entry(self, file_name, inode_id, file_type, parent_inode_id):
        '''
        Adds a new dir entry at the current directory and returns the dir entry size.
        file_type: 0 => regular file, 1 => directory file
        '''
        parent_inode = self.InodeTable.get_inode(parent_inode_id)
        name_len = len(file_name)
        struct_mask = '=hhhh{0}s'.format(name_len)
        dir_entry_size = struct.calcsize(struct_mask)
        print "Adding entry {0},{1},{2},{3},{4}".format(inode_id, dir_entry_size, name_len, file_type, file_name)
        block_data = struct.pack(struct_mask, inode_id, dir_entry_size, name_len, file_type, file_name)
        cluster_offset = int(math.ceil(parent_inode.i_size / Settings.datablock_size))
        print "At block pointer {0}, with adress {1}".format(cluster_offset, parent_inode.i_blocks[cluster_offset])
        if(cluster_offset > 1):
            data_offset = parent_inode.i_size - Settings.datablock_size
        else:
            data_offset = parent_inode.i_size
        data_offset = parent_inode.i_blocks[cluster_offset] + data_offset
        print "And data offset {0}".format(data_offset)
        #Move at start of Data Region
        self.file_object.seek(Settings.datablock_region_offset)
        #Move to the last occupied block
        self.file_object.seek(data_offset, 1)
        self.file_object.write(block_data)
        return dir_entry_size

    def read_file(self, file_name):
        "Try to read the file_name: in the current directory"

        print "READ {0}".format(file_name)
        current_inode = self.InodeTable.get_inode(self.__current_inode_id)
        data_size = current_inode.i_size
        bytes_readed = 0
        self.file_object.seek(Settings.datablock_region_offset)
        entry_mask = "=hhhh"
        while bytes_readed < data_size:
            entry_size = struct.calcsize(entry_mask)
            inode_id, rec_len, name_len, file_type = struct.unpack(
                entry_mask, self.file_object.read(entry_size))
            name_mask = "={0}s".format(name_len)
            file_name = struct.unpack(name_mask, self.file_object.read(name_len))[0]
            bytes_readed += struct.calcsize(entry_mask + name_mask[1:])
            print "Dir Entry: {0},{1},{2},{3},{4}".format(inode_id, rec_len, name_len, file_type, file_name)


    def create_file(self, file_name):
        '''
        Creates a new file and return the assigned Inode ID
        '''
        current_inode = self.InodeTable.get_inode(self.__current_inode_id)
        child_inode_id = self.InodeTable.get_free_inode_index()
        current_inode.i_size += self.__add_dir_entry(file_name, child_inode_id, 0, 0)
        self.InodeTable.set_inode(self.__current_inode_id, current_inode)
        self.InodeTable.set_inode_as_occupied(child_inode_id)
        return child_inode_id

    def create_folder(self, folder_name):
        '''
        Creates a new file and return the assigned Inode ID
        '''
        current_inode = self.InodeTable.get_inode(self.__current_inode_id)
        child_inode_id = self.InodeTable.get_free_inode_index()
        current_inode.i_size += self.__add_dir_entry(folder_name, child_inode_id, 1, 0)
        self.InodeTable.set_inode(self.__current_inode_id, current_inode)
        self.InodeTable.set_inode_as_occupied(child_inode_id)
        return child_inode_id

    @classmethod
    def bits(cls, f):
        bytes = (ord(b) for b in f.read())
        for b in bytes:
            for i in xrange(8):
                yield (b >> i) & 1
        