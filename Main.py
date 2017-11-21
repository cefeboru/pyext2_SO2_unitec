"""
 Author: Cesar Bonilla
"""
import os
import sys
from FileSystem import FileSystem

new_fs = False
file_path = "FS.ext2"
if not os.path.isfile(file_path):
    new_fs = True
    open(file_path, "wb").close()

with open(file_path, "r+b") as fs_file:
    file_system = FileSystem(fs_file, new_fs)
    if new_fs:
        file_system._create_file_system()
    """
    file_system.write_file("cesar.txt", "Hello World")
    file_system.read_file("cesar.txt")
    file_system.create_directory("test")
    file_system.list_files()
    
    file_system.read_file("test.txt")
    """
    file_system.create_file("1.txt")
    file_system.create_file("2.txt")
    file_system.create_file("3.txt")
    file_system.create_file("4.txt")
    file_system.create_file("5.txt")
    while True:
        parameters = raw_input("{0}$: ".format(file_system.working_dir))
        string_init = parameters.find('"') + 1
        string_end = parameters.find('"', string_init)
        file_content = parameters[string_init:string_end]
        parameters = parameters.replace('"'+file_content+'"', "")
        parameters = " ".join(parameters.split())
        cmd = parameters.split(" ")

        if cmd[0] == "cd":
            file_system.change_directory(cmd[1])
        elif cmd[0] == "cat":
            file_system.read_file(cmd[1])
        elif cmd[0] == "echo" and cmd[1] == ">":
            file_system.write_file(cmd[2], file_content)
        elif cmd[0] == "ls":
            file_system.list_files()
        elif cmd[0] == "mkdir":
            file_system.create_directory(cmd[1])
        elif cmd[0] == "rmdir":
            file_system.remove_directory(cmd[1])
        elif cmd[0] == "rm":
            file_system.remove_file(cmd[1])
        elif cmd[0] == "exit": 
            break