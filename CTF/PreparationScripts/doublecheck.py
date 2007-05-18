# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.
"""
Doublecheck.py:

    Doublecheck files prior to addition into the Khronos CTS. 
    Uses the Coherency Test (from coherencyPath field in ../config.txt).
    
    Doublecheck.py does the following:
    
    1) Backups and removes preexisting error logs.
    2) Search for all COLLADA files in StandardDataSets/[advanced,intermediate,basic]_badge 
       See cts.defaultDirectories for more information.
       Can exclude certain subdirectories (see cts.defaultExceptions).
       Default: The search avoids the Blessed subfolders.
    3) Runs the coherencytest on all these files, placing errors into error_log.txt (default).
    
    Revision   Changes
    
    1.1        Released to Khronos. 
               Loads and searches config.txt for coherency_path.
               Default directories correspond to badge level (see cts.defaultDirectories).
               Removed collisions in backup/archiving mechanism (see cts.backup).
               Default directories correspond to badge level.
                    
    1.0        First Version
    
    Author:    Brendan Rehon, SCEA (brendan_rehon@playstation.sony.com)
    
"""

import cts
import os
import time

# The search directories where script looks for COLLADA files.
search_directories = cts.defaultDirectories()

# A list of directories that the search should skip
exceptions = cts.defaultExceptions()

# Coherency Test options
coherency_options = [
                    ("SCHEMA", True),                # Check Schema 
                    ("CIRCULR_REFERENCE", True),     # Check for Circular References
                    ("UNIQUE_ID", True),             # Check for Unique IDs", 
                    ("COUNTS", True),                # Check Counts
                    ("FILES", True),                 # Check Files
                    ("FLOAT_ARRAY", True),           # Check Floats
                    ("LINKS", True),                 # Check Links
                    ("SKIN", True),                  # Check Skin Usage
                    ("TEXTURE", True)                # Check Texture Usage
                    ]

# Log name
log_name = os.path.normcase(r"error_log.txt")

# Should delete the old error log, or add to it?
remove_old_error_log = True

"""

Start doublecheck routine...

"""

# Backup the error log before executing commands
if os.path.exists(log_name):
    cts.backup([log_name],".txt")
    if remove_old_error_log:
        os.remove(log_name)

# Extract the coherency path from the config.txt dictionary
configDict = cts.loadConfigDictionary()
coherency_path = configDict["coherencyPath"]
configDict.clear()

# Check if coherencytest exists... if not, report the problem.
if not os.path.exists(coherency_path):
    print "Error: Cannot find Coherency Test at config.txt's listed path:\n"
    print coherency_path
    time.sleep(3)
    print "\nQuitting script..."
    time.sleep(1)
    sys.exit()

# Extract the test settings
settings = ""
ignore_all = True

for option in coherency_options:
    flag = option[1]
    
    if flag:
        if ignore_all:
            settings = (settings + " -check")
            ignore_all = False
        settings = (settings + " " + option[0])
        
if ignore_all:
    settings = (settings + " -ignore")
    for option in coherency_options:
        settings = (settings + " " + option[0])

print "----------------------------------------------------------"
print "Searching for COLLADA files...",

# Construct the list of COLLADA files
c_files = cts.findColladaFilesFromList(search_directories,exceptions)

print len(c_files),"files loaded."

print "----------------------------------------------------------"
print "Running script with the following Coherency Test commands:"
print "----------------------------------------------------------"
for x in coherency_options:
    print x[0],"=",str(x[1])
print "----------------------------------------------------------"

# Progress counter
progress = cts.ProgressCounter(len(c_files))

# Prep settings before execution
coherency_path = "\""+coherency_path+"\" "
settings = settings + " -log \""+os.path.abspath(log_name)+"\""
prev_cwd = os.getcwd()

def doublecheck(x, in_progress, in_settings):
    
    # Change working directory to the COLLADA file's path
    os.chdir(os.path.dirname(x))
    # Run coherency test on it
    os.popen("\"" + coherency_path + "\""+ os.path.basename(x) +"\""+ in_settings+"\"")
    # Change back the working directory
    os.chdir(prev_cwd)
    # Update progress counter
    in_progress.update()

print "Progress ",
# Run coherency test
[doublecheck(x, progress, settings) for x in c_files]

print
print "----------------------------------------------------------"
print "Doublecheck script completed!"
