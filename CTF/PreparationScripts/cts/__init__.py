# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.
"""

    CTS Module: A list of useful Python functions for COLLADA batch processing.
    
    Author: Brendan Rehon, SCEA (brendan_rehon@playstation.sony.com)
    
"""

import os
import shutil
import sys

MODULE_DIR = os.getcwd()
CTS_DIR = ".."

sys.path.append(CTS_DIR) # Add access to Core.* scripts
from Core.Common.FConstants import *

COLLADA_EXTENSION = ".dae"

CMD_ABS_INPUT = "\\\"\"+self.getAbsInput()+\"\\\""
CMD_ABS_OUTPUT = "\\\"\"+self.getAbsOutput()+\"\\\""
CMD_RELATIVE_INPUT = "\\\"\"+self.getRelInput()+\"\\\""
CMD_RELATIVE_OUTPUT = "\\\"\"+self.getRelOutput()+\"\\\""

CMD_INPUT = CMD_ABS_INPUT # Default value
CMD_OUTPUT = CMD_ABS_OUTPUT # Default value

def safeRawInput(in_string = None):
    """ A version of raw_input that catches EOFError, KeyboardInterrupt errors. """
    
    try:
        if in_string == None:
            return raw_input()
        
        return raw_input(in_string)
    
    except (EOFError, KeyboardInterrupt):
        print
        print "User Interrupt: Quitting script..."
        sys.exit()

def defaultDirectories():
    """ Returns a list with values from config.txt.
    
        Code below taken from Common.FTestSuite.py (__init__).
        
        returns:
            configList: A dictionary with all the values from config.txt
    """
    directories = []
    
    # Change these directories if you want to search other directories
    directories.append("basic_badge")
    directories.append("intermediate_badge")
    directories.append("advanced_badge")
    
    # Add the root directories (where the test files are supposed to be)
    root_dir = DATA_SET_DIRS[0] # Using the non-deprecated data set path in FConstants
    
    for x in range(len(directories)):
        directories[x] = os.path.join(root_dir,directories[x])
        
    return directories

def loadConfigDictionary():
    """ Returns a dictionary with values from config.txt.
    
        Code below taken from Common.FTestSuite.py (__init__).
        
        returns:
            configList: A dictionary with all the values from config.txt
    """
    configDict = {}
    if (os.path.isfile(CONFIGURATION_FILE)):
        
        f = open(CONFIGURATION_FILE)
        line = f.readline()
        
        while line:
            
            while line.count("\t\t") > 0:
                line = line.replace("\t\t", "\t")
                
            key, value = line.split("\t", 1)
            
            if configDict.has_key(key):
                print "Warning: Ignoring redefinition of configuration " + "key: " + key + "."
                continue
            
            configDict[key] = value[:-1] # remove \n
            line = f.readline()
            
        f.close()

    return configDict

def defaultExceptions():
    """ Returns a list of directories that shouldn't be searched by the
        find COLLADA files search below.
        
        returns:
            exceptions, a list of directories that shouldn't be searched for COLLADA files
    """
    exceptions = []
    exceptions.append("Blessed") # No .dae are in Blessed file directories
    # Add more exceptions here
    return exceptions

def findColladaFilesFromList(filepaths = None, exceptions = None):
    """ Return a list of COLLADA files, given several root paths.
    
        See findColladaFiles for more information.
    """
    
    if filepaths == None:
        return []
    
    all_files = []
    
    [all_files.extend(findColladaFiles(x,exceptions)) for x in filepaths]
    
    return all_files

def findColladaFiles(filePath = os.getcwd(), exceptions = None):
    """ Return a list of COLLADA files, given a root path.
        Warning: Will not check validity, just .dae extension
        
        arguments:
            filepath, root path to search from
            exceptions, a list of directories that shouldn't be searched for COLLADA files
        returns:
            filelist, a list of Collada files (i.e. files ending with .dae)
    """
    if exceptions == None:
        exceptions = []
    colladafilelist = []
    
    for root, dirs, files in os.walk(filePath):
        # Add collada files to file list
        [colladafilelist.append(os.path.join(root,x)) for x in files if x.lower().endswith(COLLADA_EXTENSION)]
        # If a directory is on the exception list, remove it
        [dirs.remove(x) for x in exceptions if x in dirs]

    #print "COLLADA file list loaded!"
    
    return colladafilelist

def backupCollada(filelist, backup_path = "backup", should_archive = True, archive_path = "archive"):
    """ Like backup, but assumes the extension is .dae """
    
    backup(filelist, COLLADA_EXTENSION, backup_path, should_archive, archive_path)

def backup(filelist, file_extension, backup_path = "backup", should_archive = True, archive_path = "archive"):
    """ Back up all files in a file list, dumping them into the backup path directory
        
        arguments:
            filelist, the list of files to be backed up (absolute file path)
            backup_path, the relative directory to copy the files. Default: "backup" directory
    """
    
    if not os.path.isdir(backup_path):
        os.mkdir(backup_path)
    
    if should_archive: # Archiving mechanism so that backups will not be continuously overwritten
        
        backup_entries = os.listdir(backup_path)
        
        if backup_entries:
            
            if not os.path.isdir(archive_path): # Does the archive path exist?
                os.mkdir(archive_path)
                curr_archive = os.path.join(archive_path,backup_path) # Start with archive/backup/
            else:
                # If archive/backup/ exists, create archive/backupN where N is unique in the archive folder
                # Heuristic: N is the number of items in the archive path
                curr_archive = os.path.join(archive_path,backup_path+str(len(os.listdir(archive_path))))
            
            if os.path.exists(curr_archive): # If archive path collision heuristic fails...
                print "Warning:",curr_archive,"exists! Renaming archive's folders..."
                # Plan A
                # If the path exists, rename every path in the archive directory to conform to heuristic
                # i.e. folder0 = backup, folder1 = backup1, etc
                archive_files = os.listdir(archive_path)
                archive_files.sort()
                # Set directory all the subsequent folder renamings are derived from
                rename_root = os.path.join(archive_path,backup_path)
                
                for x in range(len(os.listdir(archive_path))):
                    
                    old_path = os.path.join(archive_path,archive_files[x])
                    new_path = rename_root
                    
                    if x != 0:
                        new_path = new_path + str(x)
                        
                    if old_path != new_path:
                        os.rename(old_path,new_path)
                # Plan B: Give up.
                if os.path.exists(curr_archive):
                    print "Error: Folder",curr_archive,"already exists and script cannot resolve the problem."
                    print "Quitting script..."
                    sys.exit()
            
            os.mkdir(curr_archive)
            [shutil.copy2(os.path.join(backup_path,x),os.path.join(curr_archive,x)) for x in backup_entries]
            [os.remove(os.path.join(backup_path,x)) for x in backup_entries]
            
    inventory = [] # used to check if there are any backup collisions
    
    MAX_N_CHECKS = 100 
    
    for x in filelist:
        
        backupfile = os.path.join(backup_path,os.path.basename(x))
        
        counter = 0
        # This junky loop resolves backup file collisions. 
        # Tries renaming file.dae as file#.dae, where # is in [0,MAX_N_CHECKS)
        while backupfile in inventory and counter < MAX_N_CHECKS:
            backupfile = backupfile[:-len(file_extension)]+counter+file_extension
            counter = counter + 1
        
        if counter == MAX_N_CHECKS:
            print "Warning: Couldn't find a unique file ID in",MAX_N_CHECKS,"tries for", backupfile
        
        # copy original file to backup file location
        shutil.copy2(x,backupfile)
        inventory.append(backupfile)

class BatchStack:
    """ BatchStack: Data structure to keep track of temp files and their cleanup
        
        arguments:
            filepath: the original input file
    """
    def __init__(self, filepath = None):
        self.commands = []
        self.files = []
        if filepath != None:
            self.setInput(filepath)
        
    def setInput(self,filepath):
        if len(self.files) != 0:
            print "Error: Use cleanup() first. (No action performed.)"
            return
        
        self.files.append(filepath)
    
    def generateOutput(self):
        if len(self.files) == 0:
            print "Error: Use setInput(input_file) first. (No action performed)."
            return
        
        path, base = os.path.split(self.files[0])
        base = base[:-len(COLLADA_EXTENSION)]+"_temp"+str(len(self.files))+COLLADA_EXTENSION
        self.files.append(os.path.join(path,base))
    
    def getAbsOutput(self):
        if len(self.files) <= 1:
            print "Error: Use setInput(input_file) and generateOutput() first. (None returned)."
            return None
        
        return self.files[-1]
    
    def getAbsInput(self):
        n_files = len(self.files)
        
        if n_files == 0:
            print "Error: Use setInput(input_file) first. (None returned)."
            return None
        elif n_files == 1:
            print "Warning: Using generateOutput() first is recommended. (Original input file returned)."
            return self.files[0]
        
        return self.files[-2]
        
    def getRelInput(self):
        n_files = len(self.files)
        
        if n_files == 0:
            print "Error: Use setInput(input_file) first. (None returned)."
            return None
        elif n_files == 1:
            print "Warning: Using generateOutput() first is recommended. (Original input file returned)."
            return os.path.basename(self.files[0])
        
        return os.path.basename(self.files[-2])
    
    def getRelOutput(self):
        if len(self.files) <= 1:
            print "Error: Use setInput(input_file) and generateOutput() first. (None returned)."
            return None
        
        return os.path.basename(self.files[-1])
    
    def addCommand(self,exec_string):
        self.commands.append("\""+exec_string+"\"")
        
    def cleanup(self):
        while len(self.files) > 1:
            toremove = self.files.pop(-1)
            if os.path.isfile(toremove):
                os.remove(toremove)
            else:
                print "Warning: Couldn't find file:",toremove,"to remove."
                
        del self.files[0]
    
    def finish(self):
        
        # replace the original file
        if len(self.files) > 1:
            shutil.copy2(self.files[-1],self.files[0])
        
        self.cleanup()
        
    def execute(self, this_command = None):
        
        self.generateOutput()
        
        if this_command != None:
            curr_command = eval("\""+this_command+"\"")
        else:
            curr_command = eval(self.commands.pop(0))
        
        #print curr_command
        # Execute the command
        os.popen(curr_command)
        
        if not os.path.exists(self.files[-1]):
            print
            print "Error: Command did not generate an output file."
            print "Command:",curr_command
            print "Cleaning up temp files and quitting script..."
            self.cleanup()
            sys.exit()
        
class ProgressCounter:
        """
        ProgressCounter: A simple data structure that generates a text progress bar
        """
        def __init__(self, max_n_elements, n_increments = 50):
            self.reset(max_n_elements, n_increments)
        
        def reset(self, max_n_elements, n_increments = 50):
            self.total = max_n_elements
            self.counter = 0
            self.progress_increment = 1.0/n_increments
            self.p_counter = self.progress_increment
        
        def update(self):
            self.counter = self.counter + 1
            while (1.0*self.counter)/self.total >= self.p_counter:
                sys.stdout.write("*")
                self.p_counter = self.p_counter+self.progress_increment

