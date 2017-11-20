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

    def get_free_cluster(self):
        '''
        Reads and return the first cluster index that is unused.
        Returns a tuple containin the Cluster ID and cluster offset: (cluster_id, cluster_offset)
        '''
        self.file_object.seek(Settings.datablock_bitmap_offset)
        bitmap_bytes = self.file_object.read(Settings.datablock_bitmap_size)
        data = bitarray()
        data.frombytes(bitmap_bytes)
        try:
            free_block_index = data.index(True)
            offset = Settings.datablock_region_offset + (free_block_index * Settings.datablock_size)
            return (free_block_index, offset)
        except ValueError:
            raise ValueError("No more free Clusters, please delete some files")

    def change_cluster_state(self, cluster_id, state):
        '''
        Set the clusters as occupied or free, changing the bit state from 1 to 0
        '''
        self.file_object.seek(Settings.datablock_bitmap_offset)
        bitmap_bytes = self.file_object.read(Settings.datablock_bitmap_size)
        data = bitarray()
        data.frombytes(bitmap_bytes)
        try:
            data[cluster_id] = state
            self.file_object.seek(Settings.datablock_bitmap_offset)
            self.file_object.write(data.tobytes())
        except ValueError:
            raise ValueError("Unable to set cluster as occupied or free")