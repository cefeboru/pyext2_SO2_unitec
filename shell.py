import sys
import os
from time import sleep, clock
from threading import Thread
from collections import deque
from ext2 import *


class ShellError(Exception):
  """Thrown when the shell encounters an error."""
  pass


def printDirectory(directory, recursive, showAll, longList, showTypeCharacters, showInodeNums, useTimeAccess, useTimeCreation):
  """Prints the specified directory according to the given parameters."""
  if not directory.fsType == "EXT2":
    raise FilesystemNotSupportedError()
  
  q = deque([])
  q.append(directory)
  while len(q) > 0:
    d = q.popleft()
    files = []
    maxInodeLen = 0
    maxSizeLen = 0
    maxUidLen = 0
    maxGidLen = 0
    for f in d.files():
      if not showAll and f.name.startswith("."):
        continue
      if f.isDir and f.name != "." and f.name != "..":
        if recursive:
          q.append(f)
      files.append(f)
      if longList:
        maxInodeLen = max(len(str(f.inodeNum)), maxInodeLen)
        maxSizeLen = max(len(str(f.size)), maxSizeLen)
        maxUidLen = max(len(str(f.uid)), maxUidLen)
        maxGidLen = max(len(str(f.gid)), maxGidLen)
    
    files = sorted(files, key=lambda f: f.name)
    
    if recursive:
      print "{0}:".format(d.absolutePath)
    
    for f in files:
      
      if not longList:
        name = f.name
        if showTypeCharacters:
          if f.isDir:
            name = "{0}/".format(name)
          elif f.isSymlink:
            name = "{0}@".format(name)
          elif f.isRegular and f.isExecutable:
            name = "{0}*".format(name)
        print name
        
      else:
        inodeStr = ""
        name = f.name
        if showTypeCharacters:
          if f.isDir:
            name = "{0}/".format(name)
          elif f.isSymlink:
            name = "{0}@".format(name)
          elif f.isRegular and f.isExecutable:
            name = "{0}*".format(name)
        
        if f.isSymlink:
          name = "{0} -> {1}".format(name, f.getLinkedPath())
      
        
        if showInodeNums:
          inodeStr = "{0} ".format(f.inodeNum).rjust(maxInodeLen + 1)

        numLinks = "{0}".format(f.numLinks).rjust(2)
        uid = "{0}".format(f.uid).rjust(maxUidLen)
        gid = "{0}".format(f.gid).rjust(maxGidLen)
        size = "{0}".format(f.size).rjust(maxSizeLen)
        if useTimeAccess:
          time = f.timeAccessed.ljust(17)
        elif useTimeCreation:
          time = f.timeCreated.ljust(17)
        else:
          time = f.timeModified.ljust(17)

        print "{0}{1} {2} {3} {4} {5} {6} {7}".format(inodeStr, f.modeStr, numLinks, uid, gid, size, time, name)
    print


def removeFile(parentDir, rmFile, recursive = False):
  """Removes the specified file or directory from the given directory."""
  
  if recursive and rmFile.isDir:
    
    def getFilesToRemove(rmDir):
      filesToRemove = deque([])
      for f in rmDir.files():
        if f.name == "." or f.name == "..":
          continue
        if f.isDir:
          filesToRemove.extend(getFilesToRemove(f))
        filesToRemove.append((rmDir, f))
      return filesToRemove
    
    for parent,f in getFilesToRemove(rmFile):
      parent.removeFile(f)
  
  parentDir.removeFile(rmFile)

def getFileObject(fs, directory, path, followSymlinks):
  """Looks up the file object specified by the given absolute path or the path relative to the specified directory."""
  try:
    if path == "/":
      fileObject = fs.rootDir
    elif path.startswith("/"):
      fileObject = fs.rootDir.getFileAt(path[1:], followSymlinks)
    else:
      fileObject = directory.getFileAt(path, followSymlinks)
  except FileNotFoundError:
    raise FilesystemError("{0} does not exist.".format(path))
  if fileObject.absolutePath == directory.absolutePath:
    fileObject = directory
  return fileObject

def parseNewPath(fs, directory, path):
      """Parses the given absolute path or path relative to the specified directory and returns the name of a file
  and its parent directory."""
  parentDir = directory
  if path.startswith("/"):
    path = path[1:]
    parentDir = fs.rootDir
    if parentDir.absolutePath == directory.absolutePath:
      parentDir = directory
  if "/" in path:
    name = path[path.rindex("/")+1:]
    parentDir = getFileObject(fs, directory, path[:path.rindex("/")], True)
  else:
    name = path
  return (parentDir, name)

def shell(fs):
  """Enters a command-line shell with commands for operating on the specified filesystem."""
  workingDir = fs.rootDir
  print "Entered shell mode. Type 'help' for shell commands."
  
  
  def __parseInput(inputline):
    if inputline.endswith("\\") and not inputline.endswith("\\\\"):
      raise ShellError("Invalid escape sequence.")
    
    parts = deque(inputline.split())
    if len(parts) == 0:
      raise ShellError("No command specified.")
    cmd = parts.popleft()
    flags = []
    parameters = []
    
    while len(parts) > 0:
      part = parts.popleft()
      
      if "\\" in part and not part.endswith("\\"):
        raise ShellError("Invalid escape sequence.")
      
      if part.startswith("-") and len(parameters) == 0:
        flags.extend(list(part[1:]))
      
      elif part.startswith("\"") or part.startswith("\'"):
        quoteChar = part[0]
        param = part[1:]
        nextPart = part
        while not nextPart.endswith(quoteChar) and len(parts) > 0:
          nextPart = parts.popleft()
          param = "{0} {1}".format(param, nextPart)
        if not param.endswith(quoteChar):
          raise ShellError("No closing quotation found.")
        parameters.append(param[:-1])
      
      elif part.endswith("\\"):
        param = ""
        nextPart = part
        while nextPart.endswith("\\") and len(parts) > 0:
          param = "{0} {1}".format(param, nextPart[:-1])
          nextPart = parts.popleft()
        param = "{0} {1}".format(param, nextPart)
        parameters.append(param.strip())
      
      else:
        parameters.append(part)
    
    return (cmd, flags, parameters)
  
  
  while True:
    inputline = raw_input(": '{0}' >> ".format(workingDir.absolutePath)).rstrip()
    if len(inputline) == 0:
      continue
    
    try:
      parsed = __parseInput(inputline)
      cmd = parsed[0]
      flags = parsed[1]
      parameters = parsed[2]
      
      if cmd == "exit":
        break
      
      elif cmd == "ls":
        if len(parameters) == 0:
          printDirectory(workingDir, "R" in flags, "a" in flags, "l" in flags, "F" in flags,
                         "i" in flags, "u" in flags, "U" in flags)
        elif len(parameters) == 1:
          lsDir = getFileObject(fs, workingDir, parameters[0], True)
          printDirectory(lsDir, "R" in flags, "a" in flags, "l" in flags, "F" in flags,
                         "i" in flags, "u" in flags, "U" in flags)
        else:
          raise ShellError("Invalid parameters.")
        
      elif cmd == "cd":
        if len(parameters) != 1:
          raise ShellError("Invalid parameters.")
        cdDir = getFileObject(fs, workingDir, parameters[0], True)
        if not cdDir.isDir:
          raise FilesystemError("Not a directory.")
        workingDir = cdDir
      
      
      elif cmd == "mkdir":
        if len(parameters) != 1:
          raise ShellError("Invalid parameters.")
        parsed = parseNewPath(fs, workingDir, parameters[0])
        parentDir = parsed[0]
        name = parsed[1]
        parentDir.makeDirectory(name)
  
          
      elif cmd == "rm":
        if len(parameters) != 1:
          raise ShellError("Invalid parameters.")
        parsed = parseNewPath(fs, workingDir, parameters[0])
        parentDir = parsed[0]
        name = parsed[1]
        rmFile = parentDir.getFileAt(name, False)
        removeFile(parentDir, rmFile, "r" in flags)
         
        try:
          nextDir = toDir.getFileAt(name)
          if nextDir.isSymlink:
            try:
              while nextDir.isSymlink:
                nextDir = fs.rootDir.getFileAt(nextDir.getLinkedPath()[1:])
            except FileNotFoundError:
              pass
          if nextDir.isDir:
            toDir = nextDir
            name = ""
        except FileNotFoundError:
          pass
        
        if len(name) == 0:
          name = None
                
    except ShellError as e:
      print e
      continue
    except FileNotFoundError:
      print "File not found."
      continue
    except FilesystemError as e:
      print e
      continue
