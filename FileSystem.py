# -*- coding: utf-8 -*-
'''
Author: Cesar Bonilla
Module to Handle the Ext2 File System
'''

import struct
import calendar
import time
import math
import os
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
        self.inode_table = InodeTable(fs_file)
        self.cluster_table = ClusterTable(fs_file)
        self.__current_inode_id = 0
        if not create_fs:
            self.__root_inode = self.inode_table.get_root_inode()

    def read_file(self, file_name):
        is_file, inode_id = self.is_file(file_name)
        if is_file:
            inode = self.inode_table.get_inode(inode_id)
            inode.i_adate = calendar.timegm(time.gmtime())
            bytes_to_read = inode.i_size
            #How much blocks the file has assigned
            file_blocks = int(math.ceil(float(bytes_to_read) / float(Settings.datablock_size)))
            blocks_index = 0
            file_data = ''
            while bytes_to_read > 0 and blocks_index < file_blocks:
                block = inode.i_blocks[blocks_index]
                data_region_offset = Settings.datablock_region_offset
                #self.file_object.seek(data_region_offset + (block * Settings.datablock_size))
                self.file_object.seek(block)
                if bytes_to_read >= Settings.datablock_size:
                    file_data += str(self.file_object.read(Settings.datablock_region_size))
                    bytes_to_read -= Settings.datablock_region_size
                    blocks_index += 1
                else:
                    file_data += str(self.file_object.read(bytes_to_read))
                    blocks_index += 1
                    break
            print struct.unpack("={0}s".format(inode.i_size), file_data)[0]
            print inode
        else:
            print "File not found '{0}'".format(file_name)

    def write_file(self, file_name, data):
        '''
        Write text to a file, overwriting it if it exists or crating it.
        '''
        is_file, inode_id = self.is_file(file_name)
        if is_file:
            inode = self.inode_table.get_inode(inode_id)
        else:
            inode_id = self.create_file(file_name)
            inode = self.inode_table.get_inode(inode_id)
        bytes_to_write = len(data)
        #How much blocks we need to write the data
        file_blocks = int(math.ceil(float(bytes_to_write) / float(Settings.datablock_size)))
        if file_blocks > 15:
            raise ValueError("File is too big for the file system!")
        inode.i_size = bytes_to_write
        index_bytes = 0
        index_block = 0
        
        while index_bytes < bytes_to_write and index_block < file_blocks:
            block = inode.i_blocks[index_block]
            if block == 0: #Means it has no block assigned
                block_id, block_offset = self.cluster_table.get_free_cluster()
                inode.i_blocks[index_block] = block_offset
                self.cluster_table.change_cluster_state(block_id, 0)
            else:
                block_id = block
                #block_offset = Settings.datablock_region_offset + (block_id * Settings.datablock_size)
                block_offset = block
            self.file_object.seek(block_offset)
            if bytes_to_write > Settings.datablock_size:
                _data = data[index_bytes:Settings.datablock_size + 1]
                _data = struct.pack("={0}s".format(bytes_to_write), _data)
                self.file_object.write(_data)
                index_bytes += Settings.datablock_size
                index_block += 1
            else:
                _data = struct.pack("{0}s".format(bytes_to_write), data[index_bytes:])
                self.file_object.write(_data)
                index_bytes += bytes_to_write
                index_block += 1
                break
        self.inode_table.write_inode(inode_id, inode)
        print "Writed to file, inode: {0}".format(inode)

    def list_files(self):
        "Reads the current directory and returns/prints the list of files."
        print "List Files at {0}".format(self.working_dir)
        files = self.__get_files()
        files = sorted(files, key=lambda file:file.name)
        for item in files:
            inode = self.inode_table.get_inode(item.inode_id)
            if inode.i_ddate != 0:
                continue
            if inode.i_mode == 0:
                print "File: {0}".format(item.name)
            else:
                print "Folder: {0}".format(item.name)

    def create_file(self, file_name):
        '''
        Creates a new file and returns the assigned Inode ID.
        '''
        is_file, inode_id = self.is_file(file_name)
        if not is_file:
            return self.__create_file(file_name, 0)
        else:
            print "File already exists"
            return inode_id

    def create_directory(self, directory_name):
        '''
        Creates a new directory and returns the assigned Inode ID.
        '''
        if not self.is_directory(directory_name)[0]:
            created_id = self.__create_file(directory_name, 1)
            #self.__add_dir_entry(".", created_id, 1, created_id)
            #self.__add_dir_entry("..", self.__current_inode_id, 1, created_id)
            return created_id
        else:
            print "Directory already exists"
            return None

    def change_directory(self, directory_name):
        '''
        Change the current working directory.
        '''
        directory = self.is_directory(directory_name)
        if directory[0]:
            if self.working_dir == "/" and directory_name != "." :
                self.working_dir += directory_name + "/"
            else:
                self.working_dir += directory_name 
            self.__current_inode_id = directory[1]
            print "Changed directory"
            return True
        else:
            return False

    def is_directory(self, directory_name):
        '''
        Search in the current directory if the folder exists.
        Returns: (True/False, i_node_id)
        '''
        files = self.__get_files()
        for item in files:
            f_inode = self.inode_table.get_inode(item.inode_id)
            if item.name == directory_name and item.file_type == 1 and f_inode.i_ddate == 0:                
                return (True, item.inode_id)
        return (False, -1)

    def is_file(self, file_name):
        '''
        Search in the current directory if the file exists.
        Returns: (True/False, i_node_id)
        '''
        files = self.__get_files()
        for item in files:
            if item.name == file_name and item.file_type == 0:
                f_inode = self.inode_table.get_inode(item.inode_id)
                if f_inode.i_mode == 0 and f_inode.i_ddate == 0:
                    return (True, item.inode_id)
                else:
                    return (False, -1)
        return (False, -1)

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
        chunk = "a" * size
        self.file_object.write(chunk)

    def __allocate_bitmap(self, size):
        '''
        Creates a bitmap where all the bits are set to 1 and writes it to the current file.
        '''
        array = bitarray(size * 8)
        array.setall(True)
        self.file_object.write(array.tobytes())

    def __create_inode_table(self, table_len):
        '''
        Creates "table_len" Inodes into the current file.
        '''
        while table_len > 1:
            inode = Inode()
            self.file_object.write(inode.to_binary())
            table_len = table_len - 1

    def __create_root_inode(self):
        '''
        Sets the Inode & Block 0 as occupied and updates the root inode block.
        '''
        self.inode_table.change_inode_state(0, 0)
        self.cluster_table.change_cluster_state(0, 0)
        self.__root_inode = self.inode_table.get_root_inode()
        self.__current_inode_id = 0
        # TODO ADD CURRENT DIRECTORY "."

    def __create_file(self, file_name, file_type):
        '''
        Creates a new file and returns the assigned Inode ID.
        '''
        parent_inode = self.inode_table.get_inode(self.__current_inode_id)
        child_inode_id = self.inode_table.get_free_inode_index()
        parent_inode.i_size += self.__add_dir_entry(
            file_name, child_inode_id, file_type, self.__current_inode_id)
        parent_inode.i_mdate = calendar.timegm(time.gmtime())
        #Update parent folder to reflect current entries
        self.inode_table.write_inode(self.__current_inode_id, parent_inode)
        #Update inode in case it is being reused
        child_inode = self.inode_table.get_inode(child_inode_id)
        child_inode.i_ddate = 0
        child_inode.i_cdate = calendar.timegm(time.gmtime())
        child_inode.i_mode = file_type
        child_inode.i_size = 0
        free_cluster_id, free_cluster_offset = self.cluster_table.get_free_cluster()
        child_inode.i_blocks = [free_cluster_offset, 0, 0, 0, 0, 0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0]
        self.cluster_table.change_cluster_state(free_cluster_id, 0)
        self.inode_table.write_inode(child_inode_id, child_inode)
        self.inode_table.change_inode_state(child_inode_id, 0)
        return child_inode_id

    def __add_dir_entry(self, file_name, inode_id, file_type, parent_inode_id):
        '''
        Adds a new dir entry at the current directory and returns the dir entry size.
        file_type: 0 => regular file, 1 => directory file
        '''
        parent_inode = self.inode_table.get_inode(parent_inode_id)
        name_len = len(file_name)
        struct_mask = '=hhhh{0}s'.format(name_len)
        dir_entry_size = struct.calcsize(struct_mask)
        block_data = struct.pack(
            struct_mask, inode_id, dir_entry_size, name_len, file_type, file_name)
        cluster_offset = int(
            math.ceil(float(parent_inode.i_size) / float(Settings.datablock_size)))
        if cluster_offset > 1:
            data_offset = parent_inode.i_size - Settings.datablock_size
        else:
            data_offset = parent_inode.i_size
        data_offset = parent_inode.i_blocks[cluster_offset] + data_offset
        # Move at start of Data Region
        self.file_object.seek(Settings.datablock_region_offset)
        # Move to the last occupied block
        self.file_object.seek(data_offset, 1)
        self.file_object.write(block_data)
        return dir_entry_size



    def __set_dir_entries(self, dir_entries):
        '''
        Expects the list of dir_entries to be assigned to the current folder.
        '''
        try:
            inode = self.inode_table.get_inode(self.__current_inode_id)
            inode.i_size = 0
            self.inode_table.write_inode(self.__current_inode_id, inode)
            for entry in dir_entries:
                inode.i_size += self.__add_dir_entry(entry.name, entry.inode_id, entry.file_type, self.__current_inode_id)
                self.inode_table.write_inode(self.__current_inode_id, inode)
            return True
        except ValueError:
            return False

    def __get_files(self, inode_id = -1):
        '''
        Returns the files under the directory.
        '''
        if inode_id > 0:
            current_inode = self.inode_table.get_inode(inode_id)
        else:
            current_inode = self.inode_table.get_inode(self.__current_inode_id)
        files_list = list()
        data_size = current_inode.i_size
        bytes_readed = 0
        self.file_object.seek(Settings.datablock_region_offset)
        entry_mask = "=hhhh"
        while bytes_readed < data_size:
            entry_size = struct.calcsize(entry_mask)
            inode_id, rec_len, name_len, file_type = struct.unpack(
                entry_mask, self.file_object.read(entry_size))
            name_mask = "={0}s".format(name_len)
            file_name = struct.unpack(
                name_mask, self.file_object.read(name_len))[0]
            bytes_readed += struct.calcsize(entry_mask + name_mask[1:])
            dir_entry = DirEntry(inode_id, rec_len, name_len, file_type, file_name)
            files_list.append(dir_entry)
        return files_list

    def remove_file(self, file_name):
        #Current directory dir entries
        curdir_dir_entries = self.__get_files()
        for entry in curdir_dir_entries:
            if entry.name == file_name and entry.file_type == 0:
                inode = self.inode_table.get_inode(entry.inode_id)
                file_blocks = int(math.ceil(float(inode.i_size) / float(Settings.datablock_size)))
                for index in xrange(0, file_blocks):
                    self.cluster_table.change_cluster_state(inode.i_blocks[index], 1)
                inode.i_ddate = calendar.timegm(time.gmtime())
                self.inode_table.write_inode(entry.inode_id, inode)
                self.inode_table.change_inode_state(entry.inode_id, 1)
                curdir_dir_entries.remove(entry)
                print "Removed Inode: {0}".format(self.inode_table.get_inode(entry.inode_id))
        self.__set_dir_entries(curdir_dir_entries)

    def __remove_directory_rec(self, dir_name, inode_id = -1):
        previous_inode_id = self.__current_inode_id
        if inode_id > 0:
            self.__current_inode_id = inode_id
        curdir_dir_entries = self.__get_files()
        #Deleting files in directory
        for entry in curdir_dir_entries:
            if entry.file_type == 0:
                self.remove_file(entry.name)
            else:
                self.remove_directory(entry.name, entry.inode_id)
        self.__current_inode_id = previous_inode_id
    
    def remove_directory(self, dir_name):
        curdir_dir_entries = self.__get_files()
        for entry in curdir_dir_entries:
            if entry.name == dir_name:
                self.__remove_directory_rec(dir_name)
                curdir_dir_entries.remove(entry)
        self.__set_dir_entries(curdir_dir_entries)

class DirEntry(object):
    '''
    Basic structure to handle dir entries data
    '''

    def __init__(self, inode_id, rec_len, name_len, file_type, name):
        self.inode_id = inode_id
        self.rec_len = rec_len
        self.name_len = name_len
        self.file_type = file_type
        self.name = name

    def __str__(self):
        return "{0}, {1}, {2}, {3}, {4}".format(
                    self.inode_id, self.rec_len, self.name_len, self.file_type, self.name)
