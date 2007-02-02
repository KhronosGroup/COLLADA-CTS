# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

from ImageComparators.FImageComparator import *
import os
import os.path

class FByteComparator (FImageComparator):
    """The class which represents byte comparison to the testing framework.
    
    This class uses a byte by byte comparison to compare images.
    
    """
    
    def __init__(self):
        """__init__() -> FByteComparator"""
        FImageComparator.__init__(self)
    
    
    def CompareImages(self, filename1, filename2):
        """CompareImages(filename1, filename2) -> FCompareResult
        
        Implements FImageComparator.CompareImages(filename1, filename2). 
        
        The result is positive only if both files are byte by byte similar, or 
        if both files do not exist.
        
        returns:
            FCompareResult indicating the images are the same or different. 
            Only the result of FComapreResult is set; the extra is not set.
        
        """
        compareResult = FCompareResult()
        compareResult.SetResult(False)
        
        filename1 = os.path.normpath(os.path.abspath(filename1))
        filename2 = os.path.normpath(os.path.abspath(filename2))
        if (os.path.isfile(filename1)):
            if (not os.path.isfile(filename2)):
                return compareResult
        else:
            if (os.path.isfile(filename2)):
                return compareResult
            
            compareResult.SetResult(True)
            return compareResult
        
        f1 = open(filename1, "rb")
        f2 = open(filename2, "rb")
        
        block1 = f1.read(10240) # 10 KB
        block2 = f2.read(10240) # 10 KB
        
        while (block1 == block2):
            if ((len(block1) == 0) and (len(block2) == 0)):
                f1.close()
                f2.close()
                compareResult.SetResult(True)
                return compareResult
            block1 = f1.read(10240) # 10 KB
            block2 = f2.read(10240) # 10 KB
        
        f1.close()
        f2.close()
        
        return compareResult
    
    def GetMessage(self, compareResultList):
        """GetMessage(compareResultList)->str
        
        Implements FImageComparator.GetMessage(compareResultList). 
        
        The FByteComparator uses the default message.
        
        returns:
            str representing the empty string so that the CTF uses the default
            message.
        
        """
        return ""