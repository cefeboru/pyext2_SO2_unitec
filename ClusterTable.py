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
    @classmethod
    def get_next_free_cluster(cls, file_object):
        '''
        Reads and return the first cluster index that is unused.
        Returns a tuple containin the Cluster ID and cluster offset: (cluster_id, cluster_offset)
        '''
        file_object.seek(Settings.datablock_bitmap_offset)
        bitmap_bytes = file_object.read(Settings.datablock_bitmap_size)
        data = bitarray()
        data.frombytes(bitmap_bytes)
        try:
            free_inode_position = data.index(True)
            offset = Settings.datablock_region_offset + (free_inode_position * Settings.datablock_size)
            return (free_inode_position, offset)
        except ValueError:
            raise ValueError("No more free Clusters, please delete some files")

    @classmethod
    def set_cluster_as_occupied(cls, cluster_id, file_object):
        '''
        Set the clusters as occupied, changing the bit state from 1 to 0
        '''
        file_object.seek(Settings.datablock_bitmap_offset)
        bitmap_bytes = file_object.read(Settings.datablock_bitmap_size)
        data = bitarray()
        data.frombytes(bitmap_bytes)
        try:
            data[cluster_id] = 0
            file_object.seek(Settings.datablock_bitmap_offset)
            file_object.write(data.tobytes())
        except ValueError:
            raise ValueError("Unable to set inode as occupied")


