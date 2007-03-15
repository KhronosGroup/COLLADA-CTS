# Copyright (C) 2007 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

from ImageComparators.FImageComparator import *
import os
import os.path
import subprocess
import types

class FPyramidDiff (FImageComparator):
    """The class which represents PyramidDiff to the testing framework.
    
    This class uses the PyramidDiff command line interface to compare images.
    
    """
    
    TOLERANCE = 0
    DEFAULT_EXTRA = 10000
    
    def __init__(self, configDict):
        """__init__() -> FPyramidDiff
        
        arguments:
            configDict
                dict of values taken from the config.txt file with  user
                specified values.
        
        """
        FImageComparator.__init__(self, configDict)
    
    
    def CompareImages(self, filename1, filename2):
        """CompareImages(filename1, filename2) -> FCompareResult
        
        Implements FImageComparator.CompareImages(filename1, filename2). 
        
        The result is positive only if both files pass using PyramidDiff, or 
        if both files do not exist. To pass using PyramidDiff, the result
        returned must be greater than the value specifed by TOLERANCE.
        
        arguments:
            filename1
                str corresponding to a file to compare.
            filename2
                str corresponding to another file to compare.
        
        returns:
            FCompareResult indicating the images are the same or different. 
            The extra of FComapreResult is set to the value returned by 
            PyramidDiff if both files exist.
        
        """
        compareResult = FCompareResult()
        compareResult.SetResult(False)
        compareResult.SetExtra(FPyramidDiff.DEFAULT_EXTRA)
        print "----start----"
        print filename1
        print filename2
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
        
        command = ("\"" + self.configDict["pyramidDiffPath"] + "\" \"" + 
                filename1 + "\" \"" + filename2 +"\"")
        command = command.replace("\\", "\\\\")
        p = subprocess.Popen(command)
        retcode = p.wait()
        
        compareResult.SetResult(retcode <= FPyramidDiff.TOLERANCE)
        compareResult.SetExtra(retcode)
        print retcode
        print "got to end"
        return compareResult
    
    def GetMessage(self, compareResultList):
        """GetMessage(compareResultList)->str
        
        Implements FImageComparator.GetMessage(compareResultList). 
        
        The FByteComparator uses the default message.
        
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
            str representing the empty string so that the CTF uses the default
            message.
        
        """
        print compareResultList
        if (len(compareResultList) == 0): return ""
        
        if (type(compareResultList[0]) == types.ListType):
            # message for animation
            bestValue = self.__GetTotalValue(compareResultList[0])
            if (self.__GetTotalResult(compareResultList[0])):
                return ("Passed (best animation result: " + 
                        str(bestValue) + ")")
            
            for resultList in compareResultList:
                bestValue = min(bestValue, self.__GetTotalValue(resultList))
            return ("Failed (best animation result: " + 
                    str(bestValue) + ")")
        
        # message for image
        bestValue = compareResultList[0].GetExtra()
        if (compareResultList[0].GetResult()):
            return "Passed (best image result: " + str(bestValue) + ")"
        
        for result in compareResultList:
            bestValue = min(bestValue, result.GetExtra())
        return "Failed (best image result: " + str(bestValue) + ")"
    
    def __GetTotalValue(self, resultList):
        curResult = 0
        for result in resultList:
            curResult = curResult + result.GetExtra()
        return curResult
    
    def __GetTotalResult(self, resultList):
        for result in resultList:
            if (not result.GetResult()):
                return False
        return True
    
##        elif (output == FResult.PASSED_ANIMATION):
##            text = text + "Passed (Matched Animation)"
##        elif (output == FResult.FAILED_ANIMATION):
##            text = text + "Failed (No Matched Animation)"
