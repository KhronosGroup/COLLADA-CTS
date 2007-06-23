# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

import os
import os.path

import Core.Common.FUtils as FUtils

class FDataSetParser:
    def __init__(self):
        pass
    
    def GetValidFileAndDirs(self, path):
        basePath = os.path.basename(path)
        dirs = []
        files = []
        for entry in os.listdir(path):
            fullPath = os.path.join(path, entry)
            if (os.path.isdir(fullPath) and (entry[0] != ".")):
                dirs.append(fullPath)
            elif (os.path.isfile(fullPath) and 
                    (FUtils.GetProperFilename(entry) == basePath)):
                files.append(fullPath)
        
        if (len(files) > 0):
            file = files[0] # there should only be 1 file with same proper name
        else:
            file = None
        
        dirs.sort()
        
        return (file, dirs)
    