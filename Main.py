"""
 Author: Cesar Bonilla
"""
import os
from FileSystem import FileSystem
from Settings import Settings
from InodeTable import InodeTable
from ClusterTable import ClusterTable

with open("FS_test.ext2", "r+b") as fs_file:
    file_system = FileSystem(fs_file)
    file_system._create_file_system()

with open("FS_test.ext2", "r+b") as fs_file:
    file_system = FileSystem(fs_file)
    #Test InodeTable > Get Root Inode
    root_inode = file_system.InodeTable.get_inode(1)
    print "Root Inode: {0}".format(root_inode)
    #Testing InodeTable > Get Free Inode
    free_inode = file_system.InodeTable.get_free_inode_index()
    print "First free inode is in index {0}".format(free_inode)
    #Testing Cluster Table > Get free cluster
    free_cluster, cluster_offset = file_system.ClusterTable.get_next_free_cluster()
    print "Free Cluster should be 1, is {0}".format(free_cluster)
    print "Free Cluster offset is {0}".format(cluster_offset)
