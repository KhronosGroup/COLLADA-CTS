# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

class FCompareResult:
    """Class representing result from FImageComparator."""
    def __init__(self):
        self.__extra = None
        self.__result = False
    
    def SetExtra(self, extra):
        self.__extra = extra
    
    def SetResult(self, result):
        self.__result = result
    
    def GetExtra(self):
        return self.__extra
    
    def GetResult(self):
        return self.__result

class FImageComparator:
    """Abstract class for image comparators for testing framework."""

    def __init__(self):
        pass
    
    def CompareImages(self, filename1, filename2):
        """CompareImages(filename1, filename2) -> FCompareResult
        
        Compares two images specified in the filenames. (It must be overriden 
        by any implementations of image comparators.)
        
        arguments:
            filename1
                str corresponding to a file to compare.
            filename2
                str corresponding to another file to compare.
        returns:
            FCompareResult representing the result of the comparison
        
        """
        raise NotImplementedError, "FImageComparator.CompareImages()"
    
    def GetMessage(self, compareResultList):
        """GetMessage(compareResultList)->str
        
        Gets a message from a list of FCompareResult that this FImageComparator
        generated from CompareImages to be displayed in the results column of 
        the CTF.
        
        arguments:
            compareResultList
                list of FCompareResult that this FImageComparator generated for
                a given image/animation. If it is an image it will be in the
                form [FCompareResult1, FCompareResult2, ...] for each blessed
                image there is. If it is an animation, it will be in the form
                [[FCompareResult1, FCompraeResult2,...],...] for each blessed
                animation and which FCompareResult is an image in that 
                animation.
        returns:
            str representing what will be shown in the result column of the
            CTF. Empty string ("") will be interpreted as use the default 
            message.
        
        """
        return ""
    