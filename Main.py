from FileSystem import FileSystem
from Settings import Settings

file_system = FileSystem("FS.ext2")
file_system._create_file_system(file_system.filesystem_path)

#Testing InodeTable
from InodeTable import InodeTable

with open("FS.ext2", "rb") as fs_file:
    fs_file.seek(Settings.inode_bitmap_offset)
    position = InodeTable.get_first_free_inode(fs_file)
    print "The first inode empty is in {0} position".format(position)
