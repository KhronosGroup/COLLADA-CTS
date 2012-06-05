# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import cPickle
import os.path

from Core.Common.FSerializable import *

class FSerializer:
    
    """An object that can save and load a FSerializable."""
    
    def __init__(self):
        """__init() -> FSerializer
        
        Creates the FSerializer.
        
        """
        pass
    
    def Save(self, object, filename, overwrite = True):
        """Save(object, filename, overwrite = True) -> None
        
        Saves a FSerializable to a filen.
        
        arguments:
            object
                FSerializable to save.
            filename
                string corresponding to absolute path of the destination to 
                save to.
            overwrite
                bool corresponding to whether to overwrite a file with the
                given filename if it already exists. True will overwrite. False
                will not save and return normally.
        
        """
        if (os.path.isfile(filename) and (not overwrite)): return
        
        file = open(filename, "w")
        cPickle.dump(object, file)
        file.close()
    
    def QuickLoad(self, filename):
        """QuickLoad(filename) -> FSerializable
        
        Loads a FSerializable from a file and returns it. This version is
        different from Load in that it doesn't call the FSerializable's 
        InitializeFromLoad method. Using this load is faster but can end up 
        with outdated or incorrect data. Use with caution!
        
        arguments:
            filename
                string corresponding to the absolute path of the file to load.
        
        returns:
            the loaded FSerializable.
        
        """
        file = open(filename, "r")
        object = cPickle.load(file)
        file.close()
        
        return object
    
    def Load(self, filename):
        """Load(filename) -> FSerializable
        
        Loads a FSerializable from a file and returns it.
        
        arguments:
            filename
                string corresponding to the absolute path of the file to load.
        
        returns:
            the loaded FSerializable.
        
        """
        file = open(filename, "r")
        object = cPickle.load(file)
        file.close()
        
        if (not isinstance(object, FSerializable)):
            print ("<FSerializer> loaded object is not FSerializable: " + 
                    str(object))
        
        object.InitializeFromLoad(filename)
        
        return object
    