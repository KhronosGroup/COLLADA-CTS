Prepare and Doublecheck Python scripts and the CTS module -- 5/18/07

Author: Brendan Rehon SCEA (brendan_rehon@playstation.sony.com)

--------------------------------------------------------------------

This package includes two Python scripts Prepare.py and Doublecheck.py.

These two scripts should be run on all COLLADA test files prior to addition into the Khronos CTS.

Using the COLLADA Refinery and its conditioners, the scripts:

1) Prepare the files by adding a copyright and removing <extra> tags.

2) Doublecheck the files for errors (using the Coherency Test).

These two scripts depend on an included Python module cts -- a collection of useful batch utilities.

--------------------------------------------------------------------

Prerequisites:

	Python 2.4 or greater 			(http://www.python.org)

	Khronos Conformance Test Suite 1.4 	(http://www.khronos.org)

	COLLADA Refinery  			(http://sourceforge.net/projects/colladarefinery)

--------------------------------------------------------------------

Getting Started:

	Prepare.py, Doublecheck.py should be a subdirectory of the main CTS 1.4 folder.
	The "cts" folder (with __init__.py) should in the same directory as Prepare.py, Doublecheck.py.
	
	Doublecheck.py requires config.txt in its parent directory with a valid coherencyPath field.
	
	Both scripts require FConstants.py (a CTS script in Core.Common) with a valid DATA_SET_DIRS field.
	
	Prepare.py requires a text file called copyright.txt. 
	If the user does not supply copyright.txt, Prepare.py will interactively help the user create it.

--------------------------------------------------------------------

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

--------------------------------------------------------------------
    
Doublecheck.py:

    Doublecheck files prior to addition into the Khronos CTS.
    Uses the Coherency Test (from the coherencyPath field in ../config.txt).
    
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