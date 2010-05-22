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
    
    DEFAULT_TOLERANCE = 5
    DEFAULT_EXTRA = 10000
    
    def __init__(self, configDict):
        """__init__() -> FPyramidDiff
        
        arguments:
            configDict
                dict of values taken from the config.txt file with  user
                specified values.
        
        """
        FImageComparator.__init__(self, configDict)
    
    
    def CompareImages(self, filename1, filename2, tolerance = DEFAULT_TOLERANCE):
        """CompareImages(filename1, filename2, tolerance = DEFAULT_TOLERANCE) -> FCompareResult
        
        Implements FImageComparator.CompareImages(filename1, filename2, tolerance). 
        
        The result is positive only if both files pass using PyramidDiff, or 
        if both files do not exist. To pass using PyramidDiff, the result
        returned must be greater than the value specifed by tolerance.
        
        arguments:
            filename1
                str corresponding to a file to compare.
            filename2
                str corresponding to another file to compare.
            tolerance
                integer corresponding to the acceptable difference
                between the two images. Not used by the FByteComparator.
        
        returns:
            FCompareResult indicating the images are the same or different. 
            The extra of FComapreResult is set to the value returned by 
            PyramidDiff if both files exist.
        
        """
        compareResult = FCompareResult()
        compareResult.SetResult(False)
        compareResult.SetExtra(FPyramidDiff.DEFAULT_EXTRA)
        
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
        
        compareResult.SetResult(retcode <= tolerance)
        compareResult.SetExtra(retcode)
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
        if (len(compareResultList) == 0): return ""
        
        if (type(compareResultList[0]) == types.ListType):
            # message for animation
            bestValue, highValue, lowValue = self.__GetTotalValue(
                    compareResultList[0])
            if (self.__GetTotalResult(compareResultList[0])):
                return ("Passed (best result: [" + str(lowValue).zfill(4) + 
                        "-" + str(highValue).zfill(4) + "]{" + str(bestValue) +
                        "})")
            
            for resultList in compareResultList:
                curBestValue, curHighValue, curLowValue = self.__GetTotalValue(
                        resultList)
                if (curBestValue < bestValue):
                    bestValue = curBestValue
                    highValue = curHighValue
                    lowValue = curLowValue
            return ("Warning (best result: [" + str(lowValue).zfill(4) + "-" + 
                    str(highValue).zfill(4) + "]{" + str(bestValue) + "})")
        
        # message for image
        bestValue = compareResultList[0].GetExtra()
        if (compareResultList[0].GetResult()):
            return ("Passed (best image result: " + 
                    str(bestValue).zfill(4) + ")")
        
        for result in compareResultList:
            bestValue = min(bestValue, result.GetExtra())
        return "Warning (best image result: " + str(bestValue).zfill(4) + ")"
    
    def __GetTotalValue(self, resultList):
        curResult = 0
        highestResult = 0
        lowestResult = 10000 # 9999 is invalid comparisons
        for result in resultList:
            curResult = curResult + result.GetExtra()
            highestResult = max(highestResult, result.GetExtra())
            lowestResult = min(lowestResult, result.GetExtra())
        return (curResult, highestResult, lowestResult)
    
    def __GetTotalResult(self, resultList):
        for result in resultList:
            if (not result.GetResult()):
                return False
        return True
