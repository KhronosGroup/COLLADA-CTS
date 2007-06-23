# Copyright (C) 2006 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

class FSerializable:
    
    """An object that can be saved and loaded using an FSerializer."""
    
    def __init__(self):
        """__init__() -> FSerializable
        
        Creates a FSerializable.
        
        """
        pass
    
    def InitializeFromLoad(self, filename):
        """InitializeFromLoad(filename) -> None
        
        Called after loaded in case there is some needed initialization.
        
        arguments:
            filename
                string corresponding to the absolute path of the file that this
                object was loaded from.
        
        """
        raise NotImplementedError, "FSerializable.InitializeFromLoad()"
    