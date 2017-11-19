"""
 Author: Cesar Bonilla
"""
import os
from FileSystem import FileSystem

new_fs = False
file_path = "FS_test.ext2"
if not os.path.isfile(file_path):
    new_fs = True
    open(file_path, "wb").close()

with open(file_path, "r+b") as fs_file:
    file_system = FileSystem(fs_file, new_fs)
    if(new_fs):
        file_system._create_file_system()
    #Test InodeTable > Get Root Inode
    root_inode = file_system.InodeTable.get_inode(0)
    print root_inode
    #Testing InodeTable > Get Free Inode
    free_inode = file_system.InodeTable.get_free_inode_index()
    print "First free inode is in index {0}".format(free_inode)
    #Testing Cluster Table > Get free cluster
    free_cluster, cluster_offset = file_system.ClusterTable.get_next_free_cluster()
    print "Free Cluster should be 1, is {0}".format(free_cluster)
    print "Free Cluster offset is {0}".format(cluster_offset)
    file_system.read_file("/")
    print "Creating new file"
    created_inode = file_system.create_file("Cesar.txt")
    print "Created inode {0}".format(created_inode)
    file_system.read_file("/")
