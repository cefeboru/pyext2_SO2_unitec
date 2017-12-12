# -*- coding: utf-8 -*-
'''
Author: Cesar Bonilla
Module to Handle the Ext2 File System
'''
import struct
import datetime
import math
from colorama import init, Fore
from bitarray import bitarray
from InodeBase import Inode
from ClusterTable import ClusterTable
from InodeTable import InodeTable
from Settings import Settings
from utilities import split_path_and_file, get_cluster_offset, get_current_time_seconds


class FileSystem(object):
    '''
    Class to Handle the Basic File system Operations as read, write, delete
    and create files. All size properties are in bytes.
    '''

    def __init__(self, fs_file, create_fs=False):
        init(autoreset=True)
        self.file_object = fs_file
        self.working_dir = ""
        self.inode_table = InodeTable(fs_file)
        self.cluster_table = ClusterTable(fs_file)
        self.__current_inode_id = 0
        if not create_fs:
            self.__root_inode = self.inode_table.get_root_inode()
        print "Blocks Bitmap Offset: {0}".format(Settings.datablock_bitmap_offset)
        print "Inodes Bitmap Offset: {0}".format(Settings.inode_bitmap_offset)
        print "Inode Table Offset: {0}".format(Settings.inode_table_offset)
        print "Data Region offset: {0}".format(Settings.datablock_region_offset)

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
        _bytes = bytearray(size)
        self.file_object.write(_bytes)

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
        self.__root_inode.i_size += self.__add_dir_entry(".", 0, 1, 0)
        self.__root_inode.i_mode = 1
        self.inode_table.write_inode(0, self.__root_inode)

    def __create_file(self, file_name, file_type, parent_id=-1):
        '''
        Creates a new file and returns the assigned Inode ID.
        '''
        if parent_id == -1:
            parent_id = self.__current_inode_id
        free_inode_id, free_inode = self.inode_table.get_free_inode()
        # Add dir entry to parent folder
        dir_entry_size = self.__add_dir_entry(
            file_name, free_inode_id, file_type, parent_id)
        parent_inode = self.inode_table.get_inode(parent_id)
        parent_inode.i_size += dir_entry_size
        parent_inode.i_mdate = get_current_time_seconds()
        # Clean inode for new file
        free_inode.i_ddate = 0
        free_inode.i_cdate = get_current_time_seconds()
        free_inode.i_mode = file_type
        free_inode.i_size = 0
        free_cluster_id = self.cluster_table.get_free_cluster()[0]
        free_inode.i_blocks = [free_cluster_id, 0,
                               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.cluster_table.change_cluster_state(free_cluster_id, 0)
        self.inode_table.change_inode_state(free_inode_id, 0)

        self.inode_table.write_inode(free_inode_id, free_inode)
        self.inode_table.write_inode(parent_id, parent_inode)
        return free_inode_id

    def __add_dir_entry(self, file_name, inode_id, file_type, folder_inode_id=-1):
        '''
        Adds a new dir entry at the current directory and returns the dir entry size.
        file_type: 0 => regular file, 1 => directory file
        '''
        if folder_inode_id == -1:
            folder_inode_id = self.__current_inode_id
        parent_inode = self.inode_table.get_inode(folder_inode_id)
        file_name_len = len(file_name)
        struct_mask = '=hhhh{0}s'.format(file_name_len)
        dir_entry_size = struct.calcsize(struct_mask)
        block_data = struct.pack(
            struct_mask, inode_id, dir_entry_size, file_name_len, file_type, file_name)
        # Get the index of the block to be used
        blocks_used = int(float(parent_inode.i_size) /
                          float(Settings.datablock_size))
        if blocks_used > 1:
            data_offset = parent_inode.i_size - Settings.datablock_size * blocks_used
        else:
            data_offset = parent_inode.i_size

        last_block_id = parent_inode.i_blocks[blocks_used]
        if parent_inode.i_size == 0:
            free_block_space = Settings.datablock_size
        else:
            free_block_space = (blocks_used + 1) * \
                Settings.datablock_size - parent_inode.i_size
        print "Current block has {0} of free space".format(free_block_space)
        if dir_entry_size > free_block_space:
            print "Will use a new block to allocate"
            free_block_id, block_offset = self.cluster_table.get_free_cluster()
            parent_inode.i_blocks[blocks_used + 1] = free_block_id
            self.cluster_table.change_cluster_state(free_block_id, 0)
            data_offset = block_offset
        else:
            block_offset = get_cluster_offset(last_block_id)
            data_offset += block_offset

        self.file_object.seek(data_offset)
        print "Writing dir entry of size {0} to offset {1}".format(dir_entry_size, data_offset)
        self.file_object.write(block_data)
        self.inode_table.write_inode(folder_inode_id, parent_inode)
        return dir_entry_size

    def __get_files(self, dir_inode_id=0):
        '''
        Returns all the files under the directory, even the deleted ones.
        '''
        backup_inode_id = self.__current_inode_id
        if dir_inode_id > 0:
            self.__current_inode_id = dir_inode_id
        current_inode = self.inode_table.get_inode(self.__current_inode_id)
        files_list = list()
        blocks_used = float(current_inode.i_size) / \
            float(Settings.datablock_size)
        blocks_used = int(math.ceil(blocks_used))
        for i in xrange(0, blocks_used):
            block_index = current_inode.i_blocks[i]
            entries = self.__read_block_dir_entries(block_index)
            files_list += entries
        self.__current_inode_id = backup_inode_id
        return files_list

    def __read_block_dir_entries(self, block):
        "Returns the list of direntries in the block"
        files_list = list()
        block_offset = get_cluster_offset(block)
        self.file_object.seek(block_offset)
        entry_mask = "=hhhh"
        bytes_readed = 0
        while bytes_readed < Settings.datablock_size:
            entry_size = struct.calcsize(entry_mask)
            inode_id, rec_len, name_len, file_type = struct.unpack(
                entry_mask, self.file_object.read(entry_size))
            name_mask = "={0}s".format(name_len)
            file_name = struct.unpack(
                name_mask, self.file_object.read(name_len))[0]
            bytes_readed += struct.calcsize(entry_mask + name_mask[1:])
            if rec_len != 0 and rec_len < 60:
                dir_entry = DirEntry(
                    inode_id, rec_len, name_len, file_type, file_name)
                files_list.append(dir_entry)
        return files_list

    def read_file(self, file_name):
        "Interface to read a file by name"
        is_file, inode_id = self.is_file(file_name)
        print "reading file {0}, is file?: {1}".format(file_name, is_file)
        if is_file:
            inode = self.inode_table.get_inode(inode_id)
            inode.i_adate = get_current_time_seconds()
            bytes_to_read = inode.i_size
            print "file size is: {0}".format(bytes_to_read)
            # How much blocks the file has assigned
            file_blocks = int(
                math.ceil(float(bytes_to_read) / float(Settings.datablock_size)))
            if file_blocks >= 14:
                indirect_blocks = self.inode_table.get_indirect_blocks(inode.i_blocks[14]) 
            index = 0
            file_data = ''
            while bytes_to_read > 0 and index < file_blocks:
                print "Bytes to read: {0}".format(bytes_to_read)
                block = inode.i_blocks[index] if index < 14 else indirect_blocks[index - 14]
                data_region_offset = Settings.datablock_region_offset
                seek_position = data_region_offset + (block * Settings.datablock_size)
                print "Reading block {0} at position {1}".format(block, seek_position)
                self.file_object.seek(seek_position)
                if bytes_to_read > Settings.datablock_size:
                    file_data += self.file_object.read(Settings.datablock_size)
                    bytes_to_read -= Settings.datablock_size
                    index += 1
                else:
                    file_data += self.file_object.read(bytes_to_read)
                    bytes_to_read = 0
                    index += 1
                    break
            print "Data len: {0}".format(len(str(file_data)))
            print struct.unpack("={0}s".format(inode.i_size), file_data)[0]
        else:
            print "File not found '{0}'".format(file_name)

    def write_file(self, file_name, data, append=False):
        '''
        Write text to a file, overwriting it if it exists or creating it.
        '''
        if append:
            self.__append_to_file(file_name, data)
        else:
            self.__write_to_file(file_name, data)

    def __append_to_file(self, file_name, data):
        "Internal function to append data to a file"
        is_file, inode_id = self.is_file(file_name)
        print "Inode: {0}".format(str(inode_id))
        if is_file:
            inode = self.inode_table.get_inode(inode_id)
        else:
            inode_id = self.create_file(file_name)
            inode = self.inode_table.get_inode(inode_id)
        bytes_to_write = len(data)
        print "Will append {0} bytes to file {1}".format(bytes_to_write, file_name)
        block_size = float(Settings.datablock_size)
        required_blocks = int(math.ceil(float(bytes_to_write) / block_size))
        last_used_block_index = inode.i_size / Settings.datablock_size
        if last_used_block_index + required_blocks > Settings.max_indirect_blocks + 14:
            print "File is to big for FileSystem"
            return
        indirect_blocks = [0] * Settings.max_indirect_blocks if last_used_block_index < 14 else \
                          self.inode_table.get_indirect_blocks(inode.i_blocks[14])
        writen_bytes = 0
        index = last_used_block_index
        while writen_bytes < bytes_to_write:
            if index < 14:
                block_id = inode.i_blocks[index]
                block_offset = get_cluster_offset(block_id)
                if block_id == 0: #Means it has no block assigned
                    block_id, block_offset = self.cluster_table.get_free_cluster()
                    inode.i_blocks[index] = block_id
                    self.cluster_table.change_cluster_state(block_id, 0)
                else:
                    block_offset = get_cluster_offset(block_id)
            elif index == 14:
                print "First Indirect Node"
                indirect_pointer = inode.i_blocks[index]
                if indirect_pointer == 0:#Assign a cluster to store the indirect blocks
                    print "A"
                    inode.i_blocks[index] = self.cluster_table.get_free_cluster()[0]
                    self.cluster_table.change_cluster_state(inode.i_blocks[index], 0)
                    block_id, block_offset = self.cluster_table.get_free_cluster()
                    indirect_blocks[0] = block_id
                    self.cluster_table.change_cluster_state(block_id, 0)
                else:
                    print "B"
                    indirect_blocks = self.inode_table.get_indirect_blocks(indirect_pointer)
                    block_id = indirect_blocks[0]
                    block_offset = get_cluster_offset(block_id)
                    if block_id == 0: #Means it has no block assigned
                        block_id, block_offset = self.cluster_table.get_free_cluster()
                        indirect_blocks[0] = block_id
                        self.cluster_table.change_cluster_state(block_id, 0)
            else:
                print "Indirect Node"
                block_id = indirect_blocks[index - 14]
                block_offset = get_cluster_offset(block_id)
                if block_id == 0: #Means it has no block assigned
                    block_id, block_offset = self.cluster_table.get_free_cluster()
                    indirect_blocks[index - 14] = block_id
                    self.cluster_table.change_cluster_state(block_id, 0)
            print "Will write data to block {0}".format(block_id)
            block_free_space = (index + 1) * Settings.datablock_size - inode.i_size
            if block_free_space <= 0:
                index += 1
                continue
            seek_position = block_offset + (Settings.datablock_size - block_free_space)
            self.file_object.seek(seek_position)
            print "Writing data to block {0} with offset {1}".format(block_id, seek_position)
            if bytes_to_write - writen_bytes >= block_free_space:
                start = writen_bytes
                end = writen_bytes + block_free_space
                _data = data[start:end]
                print "Data[{0},{1}]: {2}".format(start, end, _data)
                _data = struct.pack("={0}s".format(block_free_space), _data)
                self.file_object.write(_data)
                writen_bytes += block_free_space
                inode.i_size += block_free_space
                index += 1
            else:
                print "SDASDASDASDASD"
                data_segment = data[writen_bytes:]
                print "Data: {0}".format(data_segment)
                _data = struct.pack("{0}s".format(len(data_segment)), data_segment)
                self.file_object.write(_data)
                writen_bytes += len(data_segment)
                inode.i_size += len(data_segment)
                index += 1
                break
        self.inode_table.write_inode(inode_id, inode)
        print "indirect nodes {0}".format(", ".join(str(x) for x in indirect_blocks))
        self.inode_table.set_indirect_blocks(inode.i_blocks[14], indirect_blocks)

    def __write_to_file(self, file_name, data):
        "Internal function to write data to a file and overwrite current data"
        is_file, inode_id = self.is_file(file_name)
        if is_file:
            inode = self.inode_table.get_inode(inode_id)
        else:
            inode_id = self.create_file(file_name)
            inode = self.inode_table.get_inode(inode_id)
        bytes_to_write = len(data)
        print "Will write {0} bytes to file {1}".format(bytes_to_write, file_name)
        #How much blocks we need to write the data
        required_blocks = int(math.ceil(float(bytes_to_write) / float(Settings.datablock_size)))
        if required_blocks > Settings.max_indirect_blocks + 14:
            print "File is too big for the file system!"
        indirect_blocks = [0] * Settings.max_indirect_blocks
        writen_bytes = 0
        inode.i_size = 0
        for index in xrange(0, required_blocks):
            if index < 14:#Direct pointers
                block_id = inode.i_blocks[index]
                block_offset = get_cluster_offset(block_id)
                if block_id == 0: #Means it has no block assigned
                    block_id, block_offset = self.cluster_table.get_free_cluster()
                    inode.i_blocks[index] = block_id
                    self.cluster_table.change_cluster_state(block_id, 0)
            elif index == 14:#First Indirect Pointer
                indirect_pointer = inode.i_blocks[index]
                if indirect_pointer == 0:#Assign a cluster to store the indirect blocks
                    inode.i_blocks[index] = self.cluster_table.get_free_cluster()[0]
                    self.cluster_table.change_cluster_state(inode.i_blocks[index], 0)
                    block_id, block_offset = self.cluster_table.get_free_cluster()
                    indirect_blocks[0] = block_id
                    self.cluster_table.change_cluster_state(block_id, 0)
                else:
                    indirect_blocks = self.inode_table.get_indirect_blocks(indirect_pointer)
                    block_id = indirect_blocks[0]
                    block_offset = get_cluster_offset(block_id)
                    if block_id == 0: #Means it has no block assigned
                        block_id, block_offset = self.cluster_table.get_free_cluster()
                        indirect_blocks[0] = block_id
                        self.cluster_table.change_cluster_state(block_id, 0)
            else:#Indirect Pointers
                block_id = indirect_blocks[index - 14]
                block_offset = get_cluster_offset(block_id)
                if block_id == 0: #Means it has no block assigned
                    block_id, block_offset = self.cluster_table.get_free_cluster()
                    indirect_blocks[0] = block_id
                    self.cluster_table.change_cluster_state(block_id, 0)
            self.file_object.seek(block_offset)
            print "Writing data to block {0} with offset {1}".format(block_id, block_offset)
            if bytes_to_write - writen_bytes >= Settings.datablock_size:
                start = writen_bytes
                end = writen_bytes + Settings.datablock_size
                _data = data[start:end]
                print "Data[{0},{1}]: {2}".format(start, end, _data)
                _data = struct.pack("={0}s".format(Settings.datablock_size), _data)
                self.file_object.write(_data)
                writen_bytes += Settings.datablock_size
                inode.i_size += Settings.datablock_size
            else:
                data_segment = data[writen_bytes:]
                print "Data: {0}".format(data_segment)
                _data = data_segment
                _data = struct.pack("{0}s".format(len(_data)), data_segment)
                self.file_object.write(_data)
                writen_bytes += len(data_segment)
                inode.i_size += len(data_segment)
        self.inode_table.write_inode(inode_id, inode)
        self.inode_table.set_indirect_blocks(inode.i_blocks[14], indirect_blocks)

    def list_files(self, inode_id=-1):
        "Reads the current directory and returns/prints the list of files."
        if inode_id == -1:
            inode_id = self.__current_inode_id
        files = self.__get_files(inode_id)
        files = sorted(files, key=lambda file: file.name)
        for item in files:
            inode = self.inode_table.get_inode(item.inode_id)
            if inode.i_ddate != 0:
                continue
            if inode.i_mode == 0:
                print "{0}{1}".format(Fore.GREEN, item.name)
            else:
                print "{0}{1}".format(Fore.BLUE, item.name)

    def list_files_long_format(self):
        "List the files using the long format"
        entries_all = self.__get_files(self.__current_inode_id)
        entries_filtered = list()
        for entry in entries_all:
            inode = self.inode_table.get_inode(entry.inode_id)
            if inode.i_ddate == 0:
                entries_filtered.append(entry)
        file_output = "{0}{1}{2}{3} 1 root root {size} {date} {name}"
        for entry in entries_filtered:
            inode = self.inode_table.get_inode(entry.inode_id)
            owner_permissions = "rwx"
            group_permission = "rwx"
            all_permissions = "r--"
            date = datetime.datetime.fromtimestamp(
                inode.i_mdate).strftime('%Y-%m-%d %H:%M:%S')
            if inode.i_mode == 0:
                entry_type = "-"
                size = inode.i_size
            elif inode.i_mode == 1:
                entry_type = "d"
                size = 0
            elif inode.i_mode == 2:
                entry_type = "l"
                size = 0
            print file_output.format(entry_type, owner_permissions, group_permission,
                                     all_permissions, size=size, date=date, name=entry.name)

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
        is_dir, inode_id = self.is_directory(directory_name)
        if not is_dir:
            created_id = self.__create_file(directory_name, 1)
            inode = self.inode_table.get_inode(created_id)
            inode.i_size += self.__add_dir_entry(".",
                                                 created_id, 1, created_id)
            self.inode_table.write_inode(created_id, inode)
            inode.i_size += self.__add_dir_entry("..",
                                                 self.__current_inode_id, 1, created_id)
            self.inode_table.write_inode(created_id, inode)
            return created_id
        else:
            print "Directory already exists"
            return inode_id

    def change_directory(self, full_path):
        '''
        Change the current working directory.
        '''
        is_dir, inode_id = self.is_directory(full_path)
        print "the dir has id: {0}".format(inode_id)
        dir_name = full_path.split('/')
        dir_name = dir_name[len(dir_name) - 1]
        if is_dir:
            if dir_name == ".":
                return True
            elif dir_name == "..":
                last = self.working_dir.rfind("/")
                if last >= 0:
                    self.working_dir = self.working_dir[:last]
            else:
                if full_path.find('/') == 0:
                    self.working_dir = full_path
                else:
                    self.working_dir += "/" + full_path
            self.__current_inode_id = inode_id
            return True
        else:
            return False

    def is_directory(self, path):
        '''
        Search in the current directory if the folder exists.
        Returns: (True/False, i_node_id)
        '''

        found = False
        print "PATH: " + path
        path = "./" + path if path.find('/') != 0 else path
        folders = path.split("/")
        inode_id = 0 if folders[0] == "" else self.__current_inode_id
        print "Before:" + str(folders)
        folders = folders[1:]
        print "After:" + str(folders)
        childs = self.__get_files(inode_id)
        for folder in folders:
            found = False
            for child in childs:
                print "is directory -> inode_id: {0}".format(inode_id)
                print "searching for {0}, comparing with {1}".format(folder, child.name)
                inode = self.inode_table.get_inode(child.inode_id)
                if child.name == folder and inode.i_mode == 1 and inode.i_ddate == 0:
                    inode_id = child.inode_id
                    childs = self.__get_files(inode_id)
                    found = True
            if not found:
                break
        return (True, inode_id) if found else (False, -1)

    def is_file(self, file_name):
        '''
        Search in the current directory if the file exists.
        Returns: (True/False, i_node_id)
        '''
        files = self.__get_files(self.__current_inode_id)
        for item in files:
            item_inode = self.inode_table.get_inode(item.inode_id)
            if item.name == file_name and item_inode.i_mode == 0 and item_inode.i_ddate == 0:
                return (True, item.inode_id)
        return (False, -1)

    def remove_file(self, file_name):
        """ Removes the file in the current folder """
        # Current directory dir entries
        curdir_dir_entries = self.__get_files(self.__current_inode_id)
        for entry in curdir_dir_entries:
            if entry.name == file_name and entry.file_type == 0:
                inode = self.inode_table.get_inode(entry.inode_id)
                self.__free_inode_blocks(inode)
                inode.i_ddate = get_current_time_seconds()
                self.inode_table.write_inode(entry.inode_id, inode)
                #self.inode_table.change_inode_state(entry.inode_id, 1)

    def __free_inode_blocks(self, inode):
        size = float(inode.i_size)
        datablock_size = float(Settings.datablock_size)
        used_blocks = int(math.ceil(size / datablock_size))
        if used_blocks >= 14:
            indirect_blocks = self.inode_table.get_indirect_blocks(inode.i_blocks[14])
        for index in xrange(0, used_blocks):
            if index < 14:
                block_id = inode.i_blocks[index]
                self.cluster_table.change_cluster_state(block_id, 1)
            elif index == 14:
                block_id = inode.i_blocks[index]
                self.cluster_table.change_cluster_state(block_id, 1)
                self.cluster_table.change_cluster_state(indirect_blocks[0], 1)
            else:
                self.cluster_table.change_cluster_state(indirect_blocks[index - 14], 1)

    def __remove_directory_rec(self, inode_id=-1):
        '''
        Internal method used to delete folder in a recursive way
        '''
        if inode_id == -1:
            inode_id = 0
        curdir_dir_entries = self.__get_files(inode_id)
        dir_inode = self.inode_table.get_inode(inode_id)
        # Deleting files in directory
        for element in curdir_dir_entries:
            if element.name in [".", ".."]:
                continue
            inode = self.inode_table.get_inode(element.inode_id)
            if inode.i_mode == 0 and inode.i_ddate == 0:
                self.remove_file(element.name)
            elif inode.i_mode == 1 and inode.i_ddate == 0:
                self.__remove_directory_rec(element.inode_id)
        dir_inode.i_ddate = get_current_time_seconds()
        self.inode_table.write_inode(inode_id, dir_inode)

    def remove_directory(self, dir_name):
        '''
        Removes the directory and its child elements
        '''
        curdir_dir_entries = self.__get_files(self.__current_inode_id)
        for entry in curdir_dir_entries:
            if entry.name == dir_name:
                self.__remove_directory_rec(entry.inode_id)


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
