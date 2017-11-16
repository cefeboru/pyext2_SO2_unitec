"File System Settings"
from InodeBase import Inode

class Settings(object):
    inode_size = Inode.i_struct_size
    datablock_size = 4096
    datablock_max_elements = 65536
    datablock_bitmap_offset = 0
    inode_max_elements = 1024
    #Properties to be set on the FILE SYSTEM start
    datablock_bitmap_size = -1
    datablock_region_size = -1
    inode_bitmap_size = -1
    inode_bitmap_offset = -1
    inode_table_size = -1
    inode_table_offset = -1
