"Module to handle all the Inode Table Operations"

from InodeBase import Inode

class InodeTable(object):
    "Inode Table API to perform Read & Write Operations"
    _offset = 0
    @classmethod
    def get_root_inode(cls, file_object):
        '''
        Get Inode at position 0
        '''
        if cls._offset == 0:
            raise ValueError("Offset has not been set")
        file_object.seek(cls._offset)
        root_inode = Inode().from_binary(file_object)
        return root_inode

    @classmethod
    def get_inode(cls, inode_id, file_object):
        '''
        Read the Inode with the specified id
        '''
        pass
    
    @classmethod
    def set_offset(cls, offset):
        '''
        Sets the table offset in bytes in the filesystem object
        '''
        cls._offset = offset