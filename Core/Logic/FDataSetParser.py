# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

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
    