# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.
"""
Prepare.py:

    Prepares files for addition into the Khronos CTS. It adds a copyright to all files and removes <extra> tags.
    
    Requires: COLLADA Refinery (http://sourceforge.net/projects/colladarefinery)
    
    Prepare.py does the following:
    
    1) Searches for copyright.txt. If copyright.txt cannot be found, the script asks the user to create it.
    2) Search for all COLLADA files in StandardDataSets/[advanced,intermediate,basic]_badge 
       See cts.defaultDirectories for more information.
       Can exclude certain subdirectories (see cts.defaultExceptions).
       Default: The search avoids the Blessed subfolders.
    3) Backs up those files into a backup directory ("backup"). 
       If files exist in the backup directory, they are placed in an archive folder's subdirectory.
    4) Executes calls to the COLLADA refinery. 
       Two calls (in 1.1): (1) Add copyright.txt (copyrighter) (2) removes <extra> tags (daestripper).
       Every call generates a new temp output file.
       A stack (cts.BatchStack) is used to track these temp files.
    5) Cleanup: The stack replaces the original input with the final output and removes all intermediate files.
    
    Revision   Changes
    
    1.1        Released to Khronos. 
               If there is no copyright.txt, the script asks the user to create one interactively.    
               Default directories correspond to badge level (see cts.defaultDirectories).
               Removed collisions in backup/archiving mechanism (see cts.backup).
               Added more error handling and sanity checks to cts.BatchStack.
               
    1.0        First Version
    
    Author:    Brendan Rehon, SCEA (brendan_rehon@playstation.sony.com)
    
"""

import cts
import os
import sys

# The search directories where script looks for COLLADA files.
search_directories = cts.defaultDirectories()

# A list of directories that the search should skip
exceptions = cts.defaultExceptions()

# Copyright text location
copyright_txt = os.path.normcase(r"copyright.txt")

# Conditioner calls used by this prepare script
# NOTE: We will add more to the copyrighter call later in the script!
copyrighter_cmd = r"copyrighter -file %s" % copyright_txt
daestrip_cmd = r"daestripper -element extra"

conditioners = []

# Define command line command for the COLLADA refinery
refinery_path = os.path.normpath(r"refinery")
refinery_cmd = "%s -i %s -o %s -x " % ( refinery_path, cts.CMD_INPUT , cts.CMD_OUTPUT )

# Define a utility for Yes/No interactive questions (may eventually get moved to cts module)
Yes, No, Invalid = 1, 0, -1
def YesOrNo(question):
    inp = cts.safeRawInput(question)
    inp = inp.lower().strip()
    if len(inp) > 0:
        if inp[0] == 'n':
            return No
        if inp[0] == 'y':
            return Yes
    return Invalid

"""

Start prepare routine...

"""

print "----------------------------------------------------------"
print "Searching for Copyright file...",
if os.path.exists(copyright_txt):
    print "found", copyright_txt
else:
    print "Cannot find",copyright_txt,'\n'
    
    while 1: # Create the copyright.txt if it isn't available
        val = YesOrNo("Do you wish to create " + copyright_txt + "? (y/n): ")
        if val == Yes:
            break
        if val == No:
            print "\nQuitting prepare script..."
            sys.exit()
    
    copyright_str = None
    
    while 1: # Let user write up the copyright file in command line.
        txt_buffer = []
        
        inp = cts.safeRawInput("----------------------------------------------------------\n"+
                        "Type the new copyright below. Press Enter twice to finish.\n"
                        +"----------------------------------------------------------\n")
        prev_valid = True
        while inp != "" or prev_valid:
        
            txt_buffer.append(inp+"\n")
        
            if inp == "":
                prev_valid = False
            else:
                prev_valid = True
        
            inp = cts.safeRawInput()
    
        val = Invalid
        
        while val == Invalid:
            val = YesOrNo("Do you wish to save the above text? (y/n): ")
            
        if val == Yes:
            copyright_str = "".join(txt_buffer[:-1])
            break
    
    # Write the copyright file...
    cf = open(copyright_txt,'w')
    cf.write(copyright_str)
    cf.close()

print "----------------------------------------------------------"
while 1:
    
    val = YesOrNo("Overwrite pre-existing copyrights? (y/n): ")
    if val == Yes:
        copyrighter_cmd = copyrighter_cmd + " -overwrite true"
        break
    if val == No:
        copyrighter_cmd = copyrighter_cmd + " -overwrite false"
        break
    
print "----------------------------------------------------------"
print "Searching for COLLADA files...",

# Construct the list of COLLADA files
c_files = cts.findColladaFilesFromList(search_directories,exceptions)
print len(c_files),"files loaded."

# Backup the COLLADA files before executing commands
cts.backupCollada(c_files)

# Setup the data structure that tracks temp file creation and cleanup
stack = cts.BatchStack()

# Setup the data structure that updates on the script's progress
progress = cts.ProgressCounter(len(c_files))

print "----------------------------------------------------------"
print "Running script with the following conditioner commands:"
print "----------------------------------------------------------"
conditioners.append(daestrip_cmd)
conditioners.append(copyrighter_cmd)

for x in conditioners:
    print x
print "----------------------------------------------------------"
print "Progress ",

def prepare(x, in_stack, in_progress):
    
    # Configure the stack with original input file
    in_stack.setInput(x)
    # Execute the commands
    [in_stack.execute(refinery_cmd + conditioner) for conditioner in conditioners]
    # Cleanup the temp files generated by the above commands
    in_stack.finish()
    # Update the progress bar
    in_progress.update()

[prepare(x, stack, progress) for x in c_files]

print 
print "----------------------------------------------------------"
print "Prepare script completed!"