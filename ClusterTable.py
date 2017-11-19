'''
Author: Cesar Bonilla
Interface to interact with the File System Clusters
'''

from Settings import Settings
from bitarray import bitarray

class ClusterTable(object):
    '''
    Interface to interact with the File System Clusters
    '''
    def __init__(self, file_object):
        self.file_object = file_object

    def get_next_free_cluster(self):
        '''
        Reads and return the first cluster index that is unused.
        Returns a tuple containin the Cluster ID and cluster offset: (cluster_id, cluster_offset)
        '''
        self.file_object.seek(Settings.datablock_bitmap_offset)
        bitmap_bytes = self.file_object.read(Settings.datablock_bitmap_size)
        data = bitarray()
        data.frombytes(bitmap_bytes)
        try:
            free_inode_position = data.index(True)
            offset = Settings.datablock_region_offset + (free_inode_position * Settings.datablock_size)
            return (free_inode_position, offset)
        except ValueError:
            raise ValueError("No more free Clusters, please delete some files")

    def set_cluster_as_occupied(self, cluster_id):
        '''
        Set the clusters as occupied, changing the bit state from 1 to 0
        '''
        self.file_object.seek(Settings.datablock_bitmap_offset)
        bitmap_bytes = self.file_object.read(Settings.datablock_bitmap_size)
        data = bitarray()
        data.frombytes(bitmap_bytes)
        try:
            data[cluster_id] = 0
            self.file_object.seek(Settings.datablock_bitmap_offset)
            self.file_object.write(data.tobytes())
        except ValueError:
            raise ValueError("Unable to set inode as occupied")

    def read_block_as_directory(self, cluster_id, size):
        '''
        Reads the block data as dir entries, returns a list of entries
        '''
        self.file_object.seek(Settings.datablock_region_offset)
        self.file_object.seek(Settings.datablock_size * cluster_id, 1)
        binary_dirs = self.file_object.read(size)

class DirEntry(object):
    def __init__(self, inode_id, rec_len, name_len, file_type, name):
        self.inode_id = inode_id
        self.rec_len = rec_len
        self.name_len = name_len
        self.file_type = file_type
        self.name = name
