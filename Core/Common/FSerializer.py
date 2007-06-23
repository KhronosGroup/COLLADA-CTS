# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

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
    