# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

class FCompareResult:
    """Class representing result from FImageComparator."""
    def __init__(self):
        """__init___() -> FCompareResult"""
        self.__extra = None
        self.__result = False
    
    def SetExtra(self, extra):
        """SetExtra(extra) -> None
        
        Sets the extra for the FCompareResult. The extra can be used by 
        implemented FImageComparator to determine the message when GetMessage
        is called. Calling GetExtra returning the extra added by SetExtra.
        
        arguments:
            extra
                obj useful for determining the message by a FImageComparator.
        
        """
        self.__extra = extra
    
    def SetResult(self, result):
        """SetResult(result) -> None
        
        Sets the result for the FCompareResult. The result indicates whether
        the comparison is the same or not.
        
        arguments:
            result
                bool representing same or not. True means sames.
        
        """
        self.__result = result
    
    def GetExtra(self):
        """GetExtra() -> obj
        
        Gets the extra added by SetExtra.
        
        returns:
            obj that was added by SetExtra.
        
        """
        return self.__extra
    
    def GetResult(self):
        """GetResult() -> bool
        
        Gets the result that was added by SetResult.
        
        return:
            bool that was set by SetResult.
        
        """
        return self.__result

class FImageComparator:
    """Abstract class for image comparators for testing framework."""

    def __init__(self, configDict):
        """__init___(configDict) -> FImageComparator
        
        arguments:
            configDict
                dict of values taken from the config.txt file with  user
                specified values.
        
        """
        self.configDict = configDict
    
    def CompareImages(self, filename1, filename2):
        """CompareImages(filename1, filename2) -> FCompareResult
        
        Compares two images specified in the filenames. (It must be overridden 
        by any implementations of image comparators.)
        
        arguments:
            filename1
                str corresponding to a file to compare.
            filename2
                str corresponding to another file to compare.
        
        returns:
            FCompareResult representing the result of the comparison.
        
        """
        raise NotImplementedError, "FImageComparator.CompareImages()"
    
    def GetMessage(self, compareResultList):
        """GetMessage(compareResultList) -> str
        
        Gets a message from a list of FCompareResult that this FImageComparator
        generated from CompareImages to be displayed in the results column of 
        the CTF. (It may be overridden by any implementations of image 
        comparators.)
        
        arguments:
            compareResultList
                list of FCompareResult that this FImageComparator generated for
                a given image/animation. If it is an image it will be in the
                form [FCompareResult1, FCompareResult2, ...] for each blessed
                image there is if none matched, or simply [FCompareResult,] if
                there is a match. If it is an animation, it will be in the form
                [[FCompareResult1, FCompraeResult2,...],...] where the inner 
                list is for each blessed animation there is and the elements of
                that list are for each image in the animation. Similarily to 
                the single image, it will be simply 
                [[FCompareResult1, FCompraeResult2,...],] if there is an 
                animation match.
        
        returns:
            str representing what will be shown in the result column of the
            CTF. Empty string ("") will be interpreted as use the default 
            message.
        
        """
        return ""
    