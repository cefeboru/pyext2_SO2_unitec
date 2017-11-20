"""
 Author: Cesar Bonilla
"""
import os
import sys
from FileSystem import FileSystem

new_fs = False
file_path = "FS_test.ext2"
if not os.path.isfile(file_path):
    new_fs = True
    open(file_path, "wb").close()

with open(file_path, "r+b") as fs_file:
    
    file_system = FileSystem(fs_file, new_fs)
    """
    if new_fs:
    file_system._create_file_system()
    file_system.write_file("cesar.txt", "Hello World")
    file_system.read_file("cesar.txt")
    file_system.create_directory("test")
    file_system.list_files()
    file_system.write_file("test.txt", "Test")
    file_system.read_file("test.txt")
    """
    while True:
        parameters = raw_input("Enter command: ")
        cmd = parameters.split(" ")
       
        if cmd[0] == "cd":
            file_system.change_directory(cmd[1])
        elif cmd[0] == "cat":
            file_system.read_file(cmd[1])
        elif cmd[0] == "ls":
            file_system.list_files()
        elif cmd[0] == "mkdir":
            file_system.create_directory(cmd[1])
        elif cmd[0] == "rmdir":
            print "Hola"
        elif cmd[0] == "rm":
            file_system.remove_file(cmd[1])
        elif cmd[0] == "exit": 
            break
            
        
        
        
        

        
        
        
        
        