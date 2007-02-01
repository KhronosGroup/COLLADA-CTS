# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

from ImageComparators.FImageComparator import *

class FByteComparator (FImageComparator):
    """The class which represents byte comparison to the testing framework.
    
    This class uses a byte by byte comparison to compare images.
    
    """
    
    def __init__(self):
        """__init__() -> FByteComparator"""
        FImageComparator.__init__(self)
    
    
    def CompareImages(self, filename1, filename2):
        """CompareImages(filename1, filename2) -> FCompareResult
        
        Implements FImageComparator.CompareImages(filename1, filename2)
        
        """
        return FCompareResult()
    
    def GetMessage(self, compareResultList):
        """GetMessage(compareResultList)->str
        
        Implements FImageComparator.GetMessage(compareResultList). For the
        FByteComparator, it tells what is the best result.
        
        """
        return "dummy message"