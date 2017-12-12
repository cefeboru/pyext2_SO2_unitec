"File System Settings"
from InodeBase import Inode

class Settings(object):
    inode_size = Inode.i_struct_size
    datablock_size = 64
    datablock_max_elements = 65536
    datablock_bitmap_offset = 0
    inode_max_elements = 1024
    datablock_bitmap_size = datablock_max_elements / 8
    datablock_region_size = datablock_max_elements * datablock_size
    inode_bitmap_size = inode_max_elements
    inode_bitmap_offset = datablock_bitmap_size
    inode_table_size = inode_size * inode_max_elements
    inode_table_offset = datablock_bitmap_size + inode_bitmap_size
    datablock_region_offset = inode_table_offset + inode_table_size
    max_indirect_blocks = int(float(datablock_size) / 4.0)
