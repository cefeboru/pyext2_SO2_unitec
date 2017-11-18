import unittest
from FileSystem import FileSystem
from InodeTable import InodeTable

class MyTest(unittest.TestCase):
    def TestGetFreeInode(self):
        print "it should create a new file system, and the first free inode should be the inode 1"
        with open("FS_test.ext2", "r+b") as test_fs:
            FileSystem(test_fs)
            position = InodeTable.get_free_inode_index(test_fs)
            self.assertEqual(position, 1)